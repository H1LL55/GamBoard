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
    // build an 11x11 grid where the perimeter represents 40 squares
    this.boardEl.innerHTML = '';
    const size = 11;
    for(let r=0;r<size;r++){
      for(let c=0;c<size;c++){
        const div = document.createElement('div');
        div.className = 'cell';
        // perimeter cells only get an index
        if(r===0 || r===size-1 || c===0 || c===size-1){
          const pos = this.coordsToIndex(r,c,size);
          div.classList.add('perimeter');
          div.dataset.index = pos;
          const label = document.createElement('div');
          label.className = 'label';
          label.textContent = this.squareLabel(pos);
          div.appendChild(label);
        } else {
          div.classList.add('center');
        }
        this.boardEl.appendChild(div);
      }
    }
    // add a single large center panel that spans the interior
    const center = document.createElement('div');
    center.className = 'board-center';
    center.innerHTML = `<div class="center-inner"><h2>GamBoard</h2><p>Roll dice, land on spaces, play mini-games.</p></div>`;
    // position the center overlay using grid lines (2..11 exclusive)
    center.style.gridColumn = '2 / 11';
    center.style.gridRow = '2 / 11';
    this.boardEl.appendChild(center);
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
    // remove existing token for player
    const existing = this.boardEl.querySelector(`.token.p${player.id}`);
    if(existing) existing.remove();
    const cell = this.boardEl.querySelector(`.cell[data-index="${player.pos}"]`);
    if(!cell) return;
    const t = document.createElement('div');
    t.className = `token p${player.id}`;
    t.title = player.name;
    // stack tokens in corners when multiple
    const count = this.players.filter(p=>p.pos===player.pos).length;
    t.style.left = (6 + (player.id*16))+'px';
    t.style.top = (6)+'px';
    cell.appendChild(t);
    // animate token appearing
    requestAnimationFrame(()=>{
      t.classList.add('appear');
    });
    setTimeout(()=>{ t.classList.remove('appear'); }, 800);
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
    player.pos = (player.pos + steps) % this.boardSize;
    this.log(`${player.name} moved from ${this.squareLabel(start)} to ${this.squareLabel(player.pos)}`);
    this.save();
    this.renderPlayers();
    this.handleLanding(player);
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
    if(label==='BlackJack'){ this.log(`${player.name} landed on Blackjack — try the mini-game.`); }
    if(label==='Slots'){ this.log(`${player.name} landed on Slots — try the mini-game.`); }
    if(label==='Roulette'){ this.log(`${player.name} landed on Roulette — try the mini-game.`); }
    if(label==='Backarat'){ this.log(`${player.name} landed on Baccarat — try the mini-game.`); }
    // basic negative money check
    if(player.money < 0){ this.log(`${player.name} is bankrupt! Removing from game.`); this.players = this.players.filter(p=>p.money>=0); if(this.current>=this.players.length) this.current=0; }
    this.save();
    this.renderPlayers();
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
