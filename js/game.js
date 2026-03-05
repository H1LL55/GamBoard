// Minimal GamBoard game engine — hotseat multiplayer, stored in localStorage
class Game {
  constructor() {
    this.boardSize = 40; // number of squares (full perimeter)
    this.players = [];
    this.current = 0;
    this.logEl = null;
    this.diceEl = null;
    this.rollBtn = null;
    this.endTurnBtn = null;
    this.boardEl = null;
    this.playersEl = null;
    this.bank = 0;

    this.init();
  }

  init(){
    this.load();
    this.cacheElements();
    this.buildBoard();
    this.bind();
    // handle return from mini-game (auto-advance if requested)
    try{
      const params = new URLSearchParams(window.location.search);
      if(params.get('return')==='board' && params.get('player')){
        const advance = params.get('advance');
        // clear querystring to avoid repeating this logic
        history.replaceState(null,'', window.location.pathname);
        this.log('Returned from mini-game.');
        if(advance==='1'){
          // advance turn once to move to next player
          setTimeout(()=> this.endTurn(), 500);
        }
      }
    }catch(e){/* ignore */}
    this.renderPlayers();
    this.log('Game ready. Add players to start.');
  }

  cacheElements(){
    this.logEl = document.getElementById('log');
    this.diceEl = document.getElementById('dice');
    this.rollBtn = document.getElementById('rollBtn');
    this.endTurnBtn = document.getElementById('endTurnBtn');
    this.boardEl = document.getElementById('board');
    this.playersEl = document.getElementById('players');
    this.addPlayerBtn = document.getElementById('addPlayerBtn');
    this.statusEl = document.getElementById('status');
    this.bankEl = document.getElementById('bank');
  }

  bind(){
    this.rollBtn.addEventListener('click', ()=>this.handleRoll());
    this.endTurnBtn.addEventListener('click', ()=>this.endTurn());
    this.addPlayerBtn.addEventListener('click', ()=>this.addPlayerPrompt());
  }

  save(){
    const payload = {players:this.players,current:this.current,bank:this.bank};
    localStorage.setItem('gamboard_state', JSON.stringify(payload));
  }

  load(){
    try{
      const raw = localStorage.getItem('gamboard_state');
      if(raw){
        const s = JSON.parse(raw);
        this.players = s.players || [];
        this.current = s.current || 0;
        this.bank = s.bank || 0;
      }
    }catch(e){console.warn('load failed',e)}
  }

  clear(){
    localStorage.removeItem('gamboard_state');
    location.reload();
  }

  addPlayerPrompt(){
    if(this.players.length >= 4){ alert('Max 4 players'); return; }
    const name = prompt('Player name (leave empty for Player ' + (this.players.length+1) + ')') || ('Player '+(this.players.length+1));
    this.players.push({name, money:1500, pos:0, inJail:false, id:this.players.length});
    this.save();
    this.renderPlayers();
    this.log(`${name} joined the game.`);
  }

  buildBoard(){
    // build circular board with tiles placed around a circle (40 tiles)
    this.boardEl.innerHTML = '';
    const tileCount = this.boardSize; // 40
    const tileSize = 84; // must match CSS .cell size
    // create tile elements
    for(let i=0;i<tileCount;i++){
      const div = document.createElement('div');
      div.className = 'cell perimeter';
      div.dataset.index = i;
      const label = document.createElement('div');
      label.className = 'label';
      label.textContent = this.squareLabel(i);
      div.appendChild(label);
      // add mini-game icon if mapped
      const mg = this.getMiniGameForIndex(i);
      if(mg){
        div.classList.add('tile-mini');
        const icon = document.createElement('div'); icon.className='mini-icon';
        if(mg.includes('black-jack')) icon.textContent = 'BJ';
        else if(mg.includes('slots')) icon.textContent = 'S';
        else if(mg.includes('roulette')) icon.textContent = 'R';
        else if(mg.includes('backarat')) icon.textContent = 'B';
        else icon.textContent = '★';
        div.appendChild(icon);
      }
      // temporarily position at 0, we'll set proper coords after appending
      div.style.left = '0px'; div.style.top = '0px';
      this.boardEl.appendChild(div);
    }

    // add a circular center panel
    const center = document.createElement('div');
    center.className = 'board-center';
    center.innerHTML = `<div class="center-inner"><h2>GamBoard</h2><p>Roll dice, land on spaces, play mini-games.</p></div>`;
    this.boardEl.appendChild(center);

    const positionTiles = ()=>{
      const rect = this.boardEl.getBoundingClientRect();
      const cx = rect.width / 2;
      const cy = rect.height / 2;
      // choose a radius leaving room for tiles and padding
      let maxRadius = Math.min(cx, cy) - 36; // leave padding
      if(maxRadius < 80) maxRadius = Math.min(cx, cy) - 12;
      // circumference and arc per tile
      const circumference = Math.max(1, 2 * Math.PI * maxRadius);
      const arc = circumference / tileCount;
      // base css tile size (from stylesheet) - try first tile element
      let cssTileSize = tileSize;
      const sample = this.boardEl.querySelector('.cell');
      if(sample){ cssTileSize = Math.max(32, Math.min(tileSize, sample.offsetWidth || tileSize)); }
      // desired tile size should not exceed available arc length (with some padding)
      const desiredTileSize = Math.min(cssTileSize, arc * 0.85);
      // final radius adjusted so tiles sit nicely (ensure positive)
      const finalRadius = Math.max( (Math.min(cx,cy) - desiredTileSize/2 - 18), 40 );

      for(let i=0;i<tileCount;i++){
        const theta = (i / tileCount) * Math.PI * 2 - Math.PI/2; // start at top
        const x = cx + finalRadius * Math.cos(theta) - desiredTileSize/2;
        const y = cy + finalRadius * Math.sin(theta) - desiredTileSize/2;
        const el = this.boardEl.querySelector(`.cell[data-index="${i}"]`);
        if(el){
          el.style.left = `${x}px`;
          el.style.top = `${y}px`;
          el.style.width = `${desiredTileSize}px`;
          el.style.height = `${desiredTileSize}px`;
          // rotate label for legibility — keep text upright by rotating opposite half-turn when needed
          const deg = theta * 180 / Math.PI;
          const label = el.querySelector('.label');
          if(label){
            // rotate so label faces outward roughly
            const rot = deg + 90;
            label.style.transform = `rotate(${rot}deg)`;
            label.style.fontSize = Math.max(9, Math.min(12, desiredTileSize/7)) + 'px';
          }
        }
      }
    };

    // call once to position now
    positionTiles();
    // recompute on resize with debounce
    let resizeTimer = null;
    window.addEventListener('resize', ()=>{
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(()=> positionTiles(), 150);
    });

    // place tokens for existing players
    this.players.forEach(p=>this.placeToken(p));
  }

  // map grid coordinates (r,c) in an 11x11 grid to perimeter index 0..39
  coordsToIndex(r,c,size){
    const last = size-1;
    if(r===last) return last - c; // bottom row: right->left -> 0..10
    if(c===0) return 10 + (last - r); // left column: bottom-1 -> 11..19
    if(r===0) return 20 + c; // top row: left->right -> 20..30
    if(c===last) return 30 + r; // right column: top+1 -> 31..39
    return -1;
  }

  squareLabel(i){
    // Monopoly-style labels (40 squares)
    const names = [
      'Go','Mediterranean Ave','Community Chest','Baltic Ave','Income Tax','Reading RR','Oriental Ave','Chance','Vermont Ave','Connecticut Ave',
      'Jail/Just Visiting','St. Charles Place','Electric Company','States Ave','Virginia Ave','Pennsylvania RR','St. James Place','Community Chest','Tennessee Ave','New York Ave',
      'Free Parking','Kentucky Ave','Chance','Indiana Ave','Illinois Ave','B. & O. RR','Atlantic Ave','Ventnor Ave','Water Works','Marvin Gardens',
      'Go To Jail','Pacific Ave','North Carolina Ave','Community Chest','Pennsylvania Ave','Short Line','Chance','Park Place','Luxury Tax','Boardwalk'
    ];
    return names[i] || `Square ${i}`;
  }

  placeToken(player){
    // place token as an absolute child of the board so we can animate movement between tiles
    // remove any existing token for this player
    const existing = this.boardEl.querySelector(`.token.p${player.id}`);
    if(existing) existing.remove();
    const cell = this.boardEl.querySelector(`.cell[data-index="${player.pos}"]`);
    if(!cell) return;
    const rectBoard = this.boardEl.getBoundingClientRect();
    const rectCell = cell.getBoundingClientRect();
    const t = document.createElement('div');
    t.className = `token p${player.id}`;
    t.title = player.name;
    // compute position relative to board
    const left = rectCell.left - rectBoard.left + (rectCell.width - 14)/2;
    const top = rectCell.top - rectBoard.top + (rectCell.height - 14)/2;
    t.style.position = 'absolute';
    t.style.left = `${left}px`;
    t.style.top = `${top}px`;
    t.style.width = '18px';
    t.style.height = '18px';
    t.style.borderRadius = '50%';
    this.boardEl.appendChild(t);
    // animate token appearing
    requestAnimationFrame(()=> t.classList.add('appear'));
    setTimeout(()=> t.classList.remove('appear'), 800);
  }

  renderPlayers(){
    this.playersEl.innerHTML = '';
    this.players.forEach((p,idx)=>{
      const el = document.createElement('div'); el.className='player';
      if(idx === this.current) el.classList.add('active');
      el.innerHTML = `<div><strong>${p.name}</strong> <small class="muted">(#${p.id})</small></div><div>${p.money}$</div>`;
      this.playersEl.appendChild(el);
      this.placeToken(p);
    });
    this.updateStatus();
  }

  updateStatus(){
    if(this.players.length===0){ this.statusEl.textContent='No players yet.'; this.rollBtn.disabled=true; this.endTurnBtn.disabled=true; }
    else{ this.statusEl.textContent = `Current: ${this.players[this.current].name}`; this.rollBtn.disabled=false; this.endTurnBtn.disabled=false; }
    this.bankEl.textContent = `Bank: ${this.bank}$`;
  }

  handleRoll(){
    const player = this.players[this.current];
    if(!player) return;
    if(player.inJail){ this.log(`${player.name} is in jail and skips roll.`); this.endTurn(); return; }
    const n = this.rollDice();
    this.diceEl.textContent = n;
    this.log(`${player.name} rolled a ${n}`);
    this.movePlayer(player,n);
  }

  rollDice(){ return Math.floor(Math.random()*6)+1; }

  movePlayer(player,steps){
    const start = player.pos;
    const endPos = (player.pos + steps) % this.boardSize;
    // animate movement along the board, then update state and handle landing
    this.animateMove(player, start, endPos).then(()=>{
      player.pos = endPos;
      this.log(`${player.name} moved from ${this.squareLabel(start)} to ${this.squareLabel(player.pos)}`);
      this.save();
      this.renderPlayers();
      this.handleLanding(player);
    }).catch(()=>{
      // fallback: immediate move
      player.pos = endPos;
      this.log(`${player.name} moved from ${this.squareLabel(start)} to ${this.squareLabel(player.pos)}`);
      this.save();
      this.renderPlayers();
      this.handleLanding(player);
    });
  }

  // animate a player's token from start index to end index (instant if same)
  animateMove(player, startIndex, endIndex){
    return new Promise((resolve)=>{
      if(startIndex === endIndex){ resolve(); return; }
      const token = this.boardEl.querySelector(`.token.p${player.id}`) || null;
      // if no token exists yet, place one without animation
      if(!token){ this.placeToken(player); resolve(); return; }
      const startCell = this.boardEl.querySelector(`.cell[data-index="${startIndex}"]`);
      const endCell = this.boardEl.querySelector(`.cell[data-index="${endIndex}"]`);
      if(!startCell || !endCell){ resolve(); return; }
      const rectBoard = this.boardEl.getBoundingClientRect();
      const rectStart = startCell.getBoundingClientRect();
      const rectEnd = endCell.getBoundingClientRect();
      const startX = rectStart.left - rectBoard.left + (rectStart.width - token.offsetWidth)/2;
      const startY = rectStart.top - rectBoard.top + (rectStart.height - token.offsetHeight)/2;
      const endX = rectEnd.left - rectBoard.left + (rectEnd.width - token.offsetWidth)/2;
      const endY = rectEnd.top - rectBoard.top + (rectEnd.height - token.offsetHeight)/2;

      // ensure token is positioned absolutely within board
      token.style.position = 'absolute';
      token.style.left = `${startX}px`;
      token.style.top = `${startY}px`;
      // apply transition for smooth travel
      token.style.transition = 'left 650ms cubic-bezier(.2,.9,.2,1), top 650ms cubic-bezier(.2,.9,.2,1)';
      // force style flush
      // eslint-disable-next-line no-unused-expressions
      token.offsetWidth;
      token.style.left = `${endX}px`;
      token.style.top = `${endY}px`;
      const onEnd = (e)=>{
        token.removeEventListener('transitionend', onEnd);
        // clear inline transition so future moves can set it
        token.style.transition = '';
        resolve();
      };
      token.addEventListener('transitionend', onEnd);
      // safety fallback: resolve after duration
      setTimeout(()=>{ try{ token.removeEventListener('transitionend', onEnd); }catch(e){} resolve(); }, 900);
    });
  }

  handleLanding(player){
    const s = player.pos;
    const label = this.squareLabel(s);
    // simple rules
    if(label==='Start'){ player.money += 200; this.log(`${player.name} collected 200$ for passing Start.`); }
    if(label==='Tax'){ player.money -= 100; this.bank += 100; this.log(`${player.name} paid 100$ tax.`); }
    if(label==='Jail'){ player.inJail = true; this.log(`${player.name} is in Jail. Wait one turn or click End Turn to skip.`); }
    if(label==='GoToJail'){ player.pos = 9; player.inJail = true; this.log(`${player.name} was sent to Jail!`); }
    if(label==='Chance'){ const r = Math.random(); if(r<0.5){ player.money += 100; this.log(`${player.name} found 100$ (Chance).`);} else { player.money -=50; this.log(`${player.name} lost 50$ (Chance).`)} }
    // mini-game redirects (open relevant mini-game page and pass player id)
    const mini = this.getMiniGameForIndex(s);
    if(mini){
      // show confirmation modal to the user before redirecting
      this.showMiniGameConfirm(player, mini, label);
      return; // wait until user confirms/cancels
    }
    // basic negative money check
    if(player.money < 0){ this.log(`${player.name} is bankrupt! Removing from game.`); this.players = this.players.filter(p=>p.money>=0); if(this.current>=this.players.length) this.current=0; }
    this.save();
    this.renderPlayers();
  }

  showMiniGameConfirm(player, mini, label){
    // ensure modal elements exist
    const modal = document.getElementById('miniConfirm');
    if(!modal){ this.log(`Opening ${mini}...`); this.save(); setTimeout(()=>{ window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&advance=1'; }, 350); return; }
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    const confirm = document.getElementById('modalConfirm');
    const cancel = document.getElementById('modalCancel');
    title.textContent = `Enter ${label}?`;
    body.textContent = `${player.name} landed on ${label}. Open the mini-game now?`;
    modal.setAttribute('aria-hidden','false');
    const onConfirm = ()=>{
      modal.setAttribute('aria-hidden','true');
      confirm.removeEventListener('click', onConfirm);
      cancel.removeEventListener('click', onCancel);
      this.save();
      // redirect and ask mini-game to return and auto-advance
      setTimeout(()=>{ window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&fromMini=' + encodeURIComponent(mini) + '&advance=1'; }, 200);
    };
    const onCancel = ()=>{
      modal.setAttribute('aria-hidden','true');
      confirm.removeEventListener('click', onConfirm);
      cancel.removeEventListener('click', onCancel);
      this.log(`${player.name} chose not to enter ${label}.`);
      // keep playing
    };
    confirm.addEventListener('click', onConfirm);
    cancel.addEventListener('click', onCancel);
  }

  // return mini-game page for a given perimeter index (or null)
  getMiniGameForIndex(i){
    // map specific indices to mini-games (adjustable)
    const map = {
      16: 'black-jack.html',
      26: 'slots.html',
      36: 'roulette.html',
      38: 'backarat.html',
      2: 'chance.html',
      17: 'chance.html',
      33: 'chance.html'
    };
    return map[i] || null;
  }

  endTurn(){
    // clear jail if they served a turn
    const player = this.players[this.current];
    if(player && player.inJail){ player.inJail = false; this.log(`${player.name} is released from jail.`); }
    this.current = (this.current + 1) % Math.max(1,this.players.length);
    this.save();
    this.updateStatus();
    this.log(`Turn: ${this.players[this.current].name}`);
  }

  log(msg){
    const time = new Date().toLocaleTimeString();
    const line = document.createElement('div'); line.textContent = `[${time}] ${msg}`;
    this.logEl.prepend(line);
  }
}

document.addEventListener('DOMContentLoaded', ()=>{
  // ensure js folder exists in repo; instantiate game
  const g = new Game();
  // expose to console for debugging
  window.GamBoard = g;
});
