// Minimal GamBoard game engine — hotseat multiplayer, stored in localStorage
class Game {
    constructor() {
        this.boardSize = 16; // number of squares (full perimeter)
        this.players = [];
        this.current = 0;
        this.gameOver = false;
        this.MIN_BET = 10; // default minimum bet for mini-games
        this.logEl = null;
        this.diceEl = null;
        this.rollBtn = null;
        this.endTurnBtn = null;
        this.boardEl = null;
        this.playersEl = null;
        this.bank = 0;

        this.init();
    }

    init() {
        this.load();
        this.cacheElements();
        this.buildBoard();
        this.initSidebarSlots();
        this.bind();
        // handle return from mini-game (auto-advance if requested)
        try {
            const params = new URLSearchParams(window.location.search);
            if (params.get('return') === 'board' && params.get('player')) {
                const returnedPlayerId = params.get('player');
                const advance = params.get('advance');
                // clear querystring to avoid repeating this logic
                history.replaceState(null, '', window.location.pathname);
                this.log('Returned from mini-game.');
                // reload latest state (mini-game may have changed money)
                this.load();
                // ensure current index points to the returning player so highlight is correct
                try {
                    const idx = this.players.findIndex(p => String(p.id) === String(returnedPlayerId));
                    if (idx !== -1) { this.current = idx; }
                    else { // if player was eliminated in the mini-game, ensure current is within bounds
                        if (this.current >= this.players.length) this.current = 0;
                    }
                } catch (e) { if (this.current >= this.players.length) this.current = 0; }
                this.renderPlayers();
                // check for game over immediately after returning
                if (this.checkGameOver()) return;
                if (advance === '1') {
                    // advance turn once to move to next player
                    setTimeout(() => this.endTurn(), 500);
                }
            }
        } catch (e) {/* ignore */ }
        this.renderPlayers();
        this.log('Game ready. Add players to start.');
    }

    // initialize the compact slot machine in the sidebar
    initSidebarSlots() {
        try {
            const sel = document.getElementById('sidebarPlayer');
            const betInput = document.getElementById('sidebarBet');
            const spinBtn = document.getElementById('sidebarSpin');
            const reels = [document.getElementById('sbR0'), document.getElementById('sbR1'), document.getElementById('sbR2')];
            const payoutEl = document.getElementById('sidebarPayout');
            if (!sel || !betInput || !spinBtn || reels.some(r => !r) || !payoutEl) return;

            const symbols = ['🍒', '🔔', '🍋', '⭐', '7'];

            const refreshPlayerOptions = () => {
                sel.innerHTML = '';
                for (const p of this.players) {
                    const opt = document.createElement('option'); opt.value = p.id; opt.textContent = `${p.name} ($${p.money})`;
                    sel.appendChild(opt);
                }
            };

            const readState = () => { try { const raw = localStorage.getItem('gamboard_state'); return raw ? JSON.parse(raw) : { players: [], current: 0, bank: 0 }; } catch (e) { return { players: [], current: 0, bank: 0 }; } };
            const saveState = (s) => { localStorage.setItem('gamboard_state', JSON.stringify(s)); };

            refreshPlayerOptions();

            const evaluate = (res, bet, playerId) => {
                // payouts: 3x7 = 50x, three of same = 10x, two of same = 2x
                const counts = {};
                for (const s of res) counts[s] = (counts[s] || 0) + 1;
                let payout = 0; if (counts['7'] === 3) payout = bet * 50; else if (Object.values(counts).includes(3)) payout = bet * 10; else if (Object.values(counts).includes(2)) payout = bet * 2; else payout = 0;
                const state = readState();
                const p = state.players.find(x => x.id == playerId);
                if (!p) { payoutEl.textContent = 'Player not found'; saveState(state); return; }
                if (payout > 0) { p.money += payout; payoutEl.textContent = `Won $${payout}`; } else { p.money -= bet; payoutEl.textContent = `Lost $${bet}`; }
                saveState(state);
                // refresh main UI
                this.load(); this.renderPlayers();
                // check for game over
                this.checkGameOver();
            };

            const spin = () => {
                const state = readState(); if (!state.players || state.players.length === 0) { alert('No players available'); return; }
                const playerId = sel.value || state.current;
                const p = state.players.find(x => x.id == playerId);
                if (!p) { alert('Invalid player'); return; }
                const bet = Math.max(1, Math.floor(Number(betInput.value) || 1));
                if (bet > p.money) { alert('Bet exceeds money'); return; }
                payoutEl.textContent = 'Spinning...'; spinBtn.disabled = true;
                const res = [];
                for (let i = 0; i < 3; i++) { res[i] = symbols[Math.floor(Math.random() * symbols.length)]; reels[i].textContent = ''; }
                reels.forEach(r => r.classList.add('spin'));
                let step = 0;
                const iv = setInterval(() => {
                    for (let i = 0; i < 3; i++) reels[i].textContent = symbols[Math.floor(Math.random() * symbols.length)];
                    step++; if (step > 18) { clearInterval(iv); for (let i = 0; i < 3; i++) { reels[i].textContent = res[i]; reels[i].classList.remove('spin'); } evaluate(res, bet, playerId); spinBtn.disabled = false; }
                }, 80);
            };

            spinBtn.addEventListener('click', spin);
            // refresh options when players change (exposed via renderPlayers)
            const origRenderPlayers = this.renderPlayers.bind(this);
            this.renderPlayers = () => {
                origRenderPlayers();
                refreshPlayerOptions();
            };
        } catch (e) { console.warn('sidebar slots init failed', e); }
    }

    cacheElements() {
        this.logEl = document.getElementById('log');
        this.diceEl = document.getElementById('dice');
        this.rollBtn = document.getElementById('rollBtn');
        this.endTurnBtn = document.getElementById('endTurnBtn');
        this.boardEl = document.getElementById('board');
        this.playersEl = document.getElementById('players');
        this.addPlayerBtn = document.getElementById('addPlayerBtn');
        this.statusEl = document.getElementById('status');
        this.bankEl = document.getElementById('bank');
        this.restartBtn = document.getElementById('restartBtn');
    }

    bind() {
        this.rollBtn.addEventListener('click', () => this.handleRoll());
        this.endTurnBtn.addEventListener('click', () => this.endTurn());
        this.addPlayerBtn.addEventListener('click', () => this.openAddPlayerModal());
        if (this.restartBtn) this.restartBtn.addEventListener('click', () => {
            if (confirm('Restart game? This will clear all progress stored in your browser.')) this.clear();
        });
    }

    save() {
        const payload = { players: this.players, current: this.current, bank: this.bank };
        localStorage.setItem('gamboard_state', JSON.stringify(payload));
    }

    load() {
        try {
            const raw = localStorage.getItem('gamboard_state');
            if (raw) {
                const s = JSON.parse(raw);
                this.players = s.players || [];
                this.current = s.current || 0;
                this.bank = s.bank || 0;
            }
        } catch (e) { console.warn('load failed', e) }
    }

    clear() {
        localStorage.removeItem('gamboard_state');
        location.reload();
    }

    openAddPlayerModal() {
        if (this.players.length >= 4) { alert('Max 4 players'); return; }
        const modal = document.getElementById('addPlayerModal');
        const input = document.getElementById('newPlayerName');
        const confirm = document.getElementById('confirmAddPlayer');
        const cancel = document.getElementById('cancelAddPlayer');
        const icons = document.querySelectorAll('.icon-opt');
        let selectedIcon = '🐶';

        input.value = '';
        modal.setAttribute('aria-hidden', 'false');

        icons.forEach(opt => {
            opt.onclick = (e) => {
                icons.forEach(o => o.classList.remove('selected'));
                e.target.classList.add('selected');
                selectedIcon = e.target.textContent;
            };
        });

        const close = () => {
            modal.setAttribute('aria-hidden', 'true');
            confirm.onclick = null; cancel.onclick = null;
        };

        cancel.onclick = close;
        confirm.onclick = () => {
            const name = input.value.trim() || ('Player ' + (this.players.length + 1));
            this.players.push({
                name, money: 500, pos: 0, inJail: false,
                id: this.players.length, icon: selectedIcon
            });
            this.save();
            this.renderPlayers();
            this.log(`${name} joined the game.`);
            close();
        };
    }

    // check for any player who has run out of money and declare game over
    checkGameOver() {
        if (this.gameOver) return true;
        for (const p of this.players) {
            if (p.money <= 0) {
                this.showGameOver(p);
                return true;
            }
        }
        return false;
    }

    showGameOver(player) {
        this.gameOver = true;
        this.log(`GAME OVER: ${player.name} has lost all their money.`);
        // disable controls
        if (this.rollBtn) this.rollBtn.disabled = true;
        if (this.endTurnBtn) this.endTurnBtn.disabled = true;
        // show modal if present
        const modal = document.getElementById('gameOverModal');
        const title = document.getElementById('gameOverTitle');
        const body = document.getElementById('gameOverBody');
        const reset = document.getElementById('gameOverReset');
        const close = document.getElementById('gameOverClose');
        if (modal && title && body && reset && close) {
            title.textContent = 'Game Over';
            body.textContent = `${player.name} has lost all their money and is eliminated.`;
            modal.setAttribute('aria-hidden', 'false');
            const onReset = () => { reset.removeEventListener('click', onReset); close.removeEventListener('click', onClose); modal.setAttribute('aria-hidden', 'true'); this.clear(); };
            const onClose = () => { reset.removeEventListener('click', onReset); close.removeEventListener('click', onClose); modal.setAttribute('aria-hidden', 'true'); };
            reset.addEventListener('click', onReset);
            close.addEventListener('click', onClose);
        }
    }

    showWinner(player) {
        this.gameOver = true;
        this.log(`GAME FINISHED: ${player.name} is the last player standing and wins!`);
        // disable controls
        if (this.rollBtn) this.rollBtn.disabled = true;
        if (this.endTurnBtn) this.endTurnBtn.disabled = true;
        // show a simple modal using existing gameOverModal UI
        const modal = document.getElementById('gameOverModal');
        const title = document.getElementById('gameOverTitle');
        const body = document.getElementById('gameOverBody');
        const reset = document.getElementById('gameOverReset');
        const close = document.getElementById('gameOverClose');
        if (modal && title && body && reset && close) {
            title.textContent = 'Winner!';
            body.textContent = `${player.name} is the last player standing and wins the game.`;
            modal.setAttribute('aria-hidden', 'false');
            const onReset = () => { reset.removeEventListener('click', onReset); close.removeEventListener('click', onClose); modal.setAttribute('aria-hidden', 'true'); this.clear(); };
            const onClose = () => { reset.removeEventListener('click', onReset); close.removeEventListener('click', onClose); modal.setAttribute('aria-hidden', 'true'); };
            reset.addEventListener('click', onReset);
            close.addEventListener('click', onClose);
        }
    }

    buildBoard() {
        // build circular board with tiles placed around a circle (40 tiles)
        this.boardEl.innerHTML = '';
        const tileCount = this.boardSize; // 40
        const tileSize = 84; // must match CSS .cell size
        // create tile elements
        for (let i = 0; i < tileCount; i++) {
            const div = document.createElement('div');
            div.className = 'cell perimeter';
            div.dataset.index = i;
            const label = document.createElement('div');
            label.className = 'label';
            label.textContent = this.squareLabel(i);
            div.appendChild(label);
            // add mini-game icon if mapped
            const mg = this.getMiniGameForIndex(i);
            if (mg) {
                div.classList.add('tile-mini');
                const icon = document.createElement('div'); icon.className = 'mini-icon';
                if (mg.includes('black-jack')) icon.textContent = 'BJ';
                else if (mg.includes('slots')) icon.textContent = 'S';
                else if (mg.includes('roulette')) icon.textContent = 'R';
                else if (mg.includes('backarat')) icon.textContent = 'B';
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

        const positionTiles = () => {
            const rect = this.boardEl.getBoundingClientRect();
            const cx = rect.width / 2;
            const cy = rect.height / 2;
            // choose a radius leaving room for tiles and padding
            let maxRadius = Math.min(cx, cy) - 36; // leave padding
            if (maxRadius < 80) maxRadius = Math.min(cx, cy) - 12;
            // circumference and arc per tile
            const circumference = Math.max(1, 2 * Math.PI * maxRadius);
            const arc = circumference / tileCount;
            // base css tile size (from stylesheet) - try first tile element
            let cssTileSize = tileSize;
            const sample = this.boardEl.querySelector('.cell');
            if (sample) { cssTileSize = Math.max(32, Math.min(tileSize, sample.offsetWidth || tileSize)); }
            // desired tile size should not exceed available arc length (with some padding)
            const desiredTileSize = Math.min(cssTileSize, arc * 0.85);
            // final radius adjusted so tiles sit nicely (ensure positive)
            const finalRadius = Math.max((Math.min(cx, cy) - desiredTileSize / 2 - 18), 40);

            // store computed positions for use during animations
            this.tilePositions = [];
            for (let i = 0; i < tileCount; i++) {
                const theta = (i / tileCount) * Math.PI * 2 - Math.PI / 2; // start at top
                const x = cx + finalRadius * Math.cos(theta) - desiredTileSize / 2;
                const y = cy + finalRadius * Math.sin(theta) - desiredTileSize / 2;
                const el = this.boardEl.querySelector(`.cell[data-index="${i}"]`);
                if (el) {
                    el.style.left = `${x}px`;
                    el.style.top = `${y}px`;
                    el.style.width = `${desiredTileSize}px`;
                    el.style.height = `${desiredTileSize}px`;
                    // rotate label for legibility — keep text upright by rotating opposite half-turn when needed
                    const deg = theta * 180 / Math.PI;
                    const label = el.querySelector('.label');
                    if (label) {
                        // rotate so label faces outward roughly
                        const rot = deg + 90;
                        label.style.transform = `rotate(${rot}deg)`;
                        label.style.fontSize = Math.max(9, Math.min(12, desiredTileSize / 7)) + 'px';
                    }
                }
                this.tilePositions[i] = { x, y, theta, cx, cy, radius: finalRadius, size: desiredTileSize };
            }
        };

        // call once to position now
        positionTiles();
        // create a tooltip element for tiles
        let tooltip = this.boardEl.querySelector('.tile-tooltip');
        if (!tooltip) { tooltip = document.createElement('div'); tooltip.className = 'tile-tooltip'; tooltip.style.display = 'none'; this.boardEl.appendChild(tooltip); }
        // attach hover listeners to show tooltip with label and mini-game info
        for (let i = 0; i < tileCount; i++) {
            const el = this.boardEl.querySelector(`.cell[data-index="${i}"]`);
            if (!el) continue;
            el.addEventListener('mouseenter', (ev) => {
                const idx = Number(el.dataset.index);
                const label = this.squareLabel(idx);
                const mg = this.getMiniGameForIndex(idx);
                tooltip.innerHTML = `<strong>${label}</strong>` + (mg ? ` <span class="mini">${mg.includes('slots') ? 'Slots' : mg.includes('black-jack') ? 'Blackjack' : mg.includes('roulette') ? 'Roulette' : mg.includes('backarat') ? 'Baccarat' : 'Mini'}</span>` : '');
                tooltip.style.display = 'block';
                const r = el.getBoundingClientRect(); const b = this.boardEl.getBoundingClientRect();
                tooltip.style.left = `${r.left - b.left + r.width / 2}px`;
                tooltip.style.top = `${r.top - b.top}px`;
            });
            el.addEventListener('mousemove', (ev) => {
                const r = el.getBoundingClientRect(); const b = this.boardEl.getBoundingClientRect();
                tooltip.style.left = `${r.left - b.left + r.width / 2}px`;
                tooltip.style.top = `${r.top - b.top}px`;
            });
            el.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
        }
        // recompute on resize with debounce
        let resizeTimer = null;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => positionTiles(), 150);
        });

        // place tokens for existing players
        this.players.forEach(p => this.placeToken(p));
    }

    // map grid coordinates (r,c) in an 11x11 grid to perimeter index 0..39
    coordsToIndex(r, c, size) {
        const last = size - 1;
        if (r === last) return last - c; // bottom row: right->left -> 0..10
        if (c === 0) return 10 + (last - r); // left column: bottom-1 -> 11..19
        if (r === 0) return 20 + c; // top row: left->right -> 20..30
        if (c === last) return 30 + r; // right column: top+1 -> 31..39
        return -1;
    }

    squareLabel(i) {
        // Monopoly-style labels (40 squares)
        const names = [
            'Welcome to the Strip', 'Lucky Chance', 'Slot Alley','Blackjack Table', 'Viva Vegas', 'Slot Palace',
            'Roulette Row',  'Baccarat Lounge',  'Blackjack Lounge', 'Lucky Chance', 'Roulette Court',
            'Poker Promenade', 'Blackjack Den', 'Mega Slots',
            'Slot Junction', 'Lucky Chance'
        ];
        return names[i] || `Square ${i}`;
    }

    placeToken(player) {
        // place token as an absolute child of the board so we can animate movement between tiles
        // remove any existing token for this player
        const existing = this.boardEl.querySelector(`.token.p${player.id}`);
        if (existing) existing.remove();
        const cell = this.boardEl.querySelector(`.cell[data-index="${player.pos}"]`);
        if (!cell) return;
        const rectBoard = this.boardEl.getBoundingClientRect();
        const rectCell = cell.getBoundingClientRect();
        const t = document.createElement('div');
        t.className = `token p${player.id}`;
        t.title = player.name;
        // compute position relative to board
        const left = rectCell.left - rectBoard.left + (rectCell.width - 18) / 2;
        const top = rectCell.top - rectBoard.top + (rectCell.height - 18) / 2;
        t.style.position = 'absolute';
        t.style.left = `${left}px`;
        t.style.top = `${top}px`;
        t.style.width = '32px';
        t.style.height = '32px';
        // inner element holds color and rotation
        const inner = document.createElement('div');
        inner.className = 'token-inner';
        inner.style.transform = 'rotate(0deg)';

        // Icon inside the token for quick identification
        inner.textContent = player.icon || '🎲';
        inner.style.fontSize = '18px';

        t.appendChild(inner);
        this.boardEl.appendChild(t);
        // animate token appearing
        requestAnimationFrame(() => t.classList.add('appear'));
        setTimeout(() => t.classList.remove('appear'), 800);
    }

    renderPlayers() {
        this.playersEl.innerHTML = '';
        this.players.forEach((p, idx) => {
            const el = document.createElement('div'); el.className = 'player';
            if (idx === this.current) el.classList.add('active');
            const icon = p.icon || '🎲';
            el.innerHTML = `<div><span class="player-icon">${icon}</span><strong>${p.name}</strong></div><div>${p.money}$</div>`;
            this.playersEl.appendChild(el);
            this.placeToken(p);
        });
        this.updateStatus();
        // update center panel with active player info
        try {
            const centerInner = this.boardEl.querySelector('.board-center .center-inner');
            if (centerInner) {
                const cur = this.players[this.current];
                if (cur) {
                    centerInner.innerHTML = `<h2>${cur.name}</h2><p>Money: <strong>${cur.money}$</strong></p><p style="margin-top:8px;color:var(--muted);font-size:13px">Position: ${this.squareLabel(cur.pos)}</p>`;
                    centerInner.classList.add('pulse');
                    setTimeout(() => centerInner.classList.remove('pulse'), 700);
                } else {
                    centerInner.innerHTML = `<h2>GamBoard</h2><p>Roll dice, land on spaces, play mini-games.</p>`;
                }
            }
        } catch (e) {/* ignore */ }
    }

    updateStatus() {
        if (this.gameOver) { this.statusEl.textContent = 'Game over.'; if (this.rollBtn) this.rollBtn.disabled = true; if (this.endTurnBtn) this.endTurnBtn.disabled = true; return; }
        if (this.players.length === 0) { this.statusEl.textContent = 'No players yet.'; this.rollBtn.disabled = true; this.endTurnBtn.disabled = true; }
        else {
            if (this.current >= this.players.length) this.current = 0;
            const cur = this.players[this.current];
            this.statusEl.textContent = `Current: ${cur ? cur.name : '—'}`;
            this.rollBtn.disabled = false; this.endTurnBtn.disabled = false;
        }
        this.bankEl.textContent = `Bank: ${this.bank}$`;
    }

    handleRoll() {
        const player = this.players[this.current];
        if (!player) return;
        if (player.inJail) { this.log(`${player.name} is in jail and skips roll.`); this.endTurn(); return; }
        // animate dice roll visually, then move
        if (!this.diceEl) { const n = this.rollDice(); this.log(`${player.name} rolled a ${n}`); this.movePlayer(player, n); return; }
        this.rollBtn.disabled = true;
        const rollDuration = 900; // ms
        this.diceEl.classList.add('rolling');
        let iv = null;
        iv = setInterval(() => { this.diceEl.textContent = Math.floor(Math.random() * 6) + 1; }, 80);
        setTimeout(() => {
            clearInterval(iv);
            this.diceEl.classList.remove('rolling');
            const n = this.rollDice();
            this.diceEl.textContent = n;
            this.log(`${player.name} rolled a ${n}`);
            // small delay so players see the final dice value
            setTimeout(() => {
                this.movePlayer(player, n);
                this.rollBtn.disabled = false;
            }, 220);
        }, rollDuration);
    }

    rollDice() { return Math.floor(Math.random() * 6) + 1; }

    movePlayer(player, steps) {
        const start = player.pos;
        const endPos = (player.pos + steps) % this.boardSize;
        // animate movement along the board, then update state and handle landing
        this.animateMove(player, start, endPos).then(() => {
            player.pos = endPos;
            this.log(`${player.name} moved from ${this.squareLabel(start)} to ${this.squareLabel(player.pos)}`);
            this.save();
            this.renderPlayers();
            this.handleLanding(player);
        }).catch(() => {
            // fallback: immediate move
            player.pos = endPos;
            this.log(`${player.name} moved from ${this.squareLabel(start)} to ${this.squareLabel(player.pos)}`);
            this.save();
            this.renderPlayers();
            this.handleLanding(player);
        });
    }

    // animate a player's token from start index to end index (instant if same)
    animateMove(player, startIndex, endIndex) {
        return new Promise((resolve) => {
            if (startIndex === endIndex) { resolve(); return; }
            const token = this.boardEl.querySelector(`.token.p${player.id}`) || null;
            if (!token) { this.placeToken(player); resolve(); return; }
            const positions = this.tilePositions;
            const tileCount = this.boardSize;
            if (!positions || positions.length !== tileCount) {
                // fallback to instant move if positions aren't ready
                const endCell = this.boardEl.querySelector(`.cell[data-index="${endIndex}"]`);
                if (endCell) { const rb = this.boardEl.getBoundingClientRect(); const re = endCell.getBoundingClientRect(); token.style.left = `${re.left - rb.left + (re.width - token.offsetWidth) / 2}px`; token.style.top = `${re.top - rb.top + (re.height - token.offsetHeight) / 2}px`; }
                resolve(); return;
            }

            const startPos = positions[startIndex];
            const steps = (endIndex - startIndex + tileCount) % tileCount;
            const anglePerStep = (2 * Math.PI) / tileCount;
            const totalAngle = steps * anglePerStep;
            const cx = startPos.cx;
            const cy = startPos.cy;
            const radius = startPos.radius;

            // ensure token starts at the exact start coords
            const startX = startPos.x + startPos.size / 2 - (token.offsetWidth / 2);
            const startY = startPos.y + startPos.size / 2 - (token.offsetHeight / 2);
            token.style.left = `${startX}px`;
            token.style.top = `${startY}px`;
            // mark token as moving for visual emphasis
            token.classList.add('moving');
            token.style.zIndex = 1000;

            const durationPerStep = 180; // ms per tile
            const duration = Math.max(300, Math.min(2200, durationPerStep * steps));
            const startAngle = startPos.theta;
            const startTime = performance.now();

            const ease = (t) => (--t) * t * t + 1; // easeOutCubic

            let rafId = null;
            const highlightTimeouts = [];
            // schedule tile pass highlights so players can see the path
            const stepsIndices = [];
            for (let k = 1; k <= steps; k++) stepsIndices.push((startIndex + k) % tileCount);
            const stepTime = duration / Math.max(1, steps);
            stepsIndices.forEach((idx, i) => {
                const to = setTimeout(() => {
                    const cell = this.boardEl.querySelector(`.cell[data-index="${idx}"]`);
                    if (cell) { cell.classList.add('passed'); }
                    // remove after a short while so trail fades
                    const rem = setTimeout(() => { if (cell) cell.classList.remove('passed'); }, Math.min(700, stepTime * 1.1));
                    highlightTimeouts.push(rem);
                }, Math.max(0, i * stepTime));
                highlightTimeouts.push(to);
            });
            const stepFn = (now) => {
                const t = Math.min(1, (now - startTime) / duration);
                const eased = ease(t);
                const angle = startAngle + eased * totalAngle;
                const x = cx + radius * Math.cos(angle) - token.offsetWidth / 2;
                const y = cy + radius * Math.sin(angle) - token.offsetHeight / 2;
                token.style.left = `${x}px`;
                token.style.top = `${y}px`;
                // rotate inner to face travel direction (tangent)
                const tangent = angle + Math.PI / 2;
                const deg = tangent * 180 / Math.PI;
                const inner = token.querySelector('.token-inner');
                if (inner) inner.style.transform = `rotate(${deg}deg)`;
                if (t < 1) { rafId = requestAnimationFrame(stepFn); }
                else {
                    if (rafId) cancelAnimationFrame(rafId);
                    token.style.zIndex = '';
                    // arrival: small bob to celebrate landing
                    token.classList.add('bob');
                    setTimeout(() => token.classList.remove('bob'), 700);
                    // remove moving state
                    token.classList.remove('moving');
                    // highlight final tile briefly
                    const endCell = this.boardEl.querySelector(`.cell[data-index="${endIndex}"]`);
                    if (endCell) { endCell.classList.add('target'); setTimeout(() => endCell.classList.remove('target'), 900); }
                    // clear any pending highlight timeouts
                    highlightTimeouts.forEach(id => clearTimeout(id));
                    if (timeoutId) clearTimeout(timeoutId);
                    resolve();
                }
            };
            rafId = requestAnimationFrame(stepFn);
            // safety timeout (in case RAF stalls) — will add bob and resolve
            let timeoutId = setTimeout(() => {
                if (rafId) cancelAnimationFrame(rafId);
                token.style.zIndex = '';
                token.classList.add('bob');
                setTimeout(() => token.classList.remove('bob'), 700);
                token.classList.remove('moving');
                highlightTimeouts.forEach(id => clearTimeout(id));
                resolve();
            }, duration + 300);
        });
    }

    handleLanding(player) {
        const s = player.pos;
        const label = this.squareLabel(s);
        // simple rules
        if (label === 'Start') { player.money += 200; this.log(`${player.name} collected 200$ for passing Start.`); }
        if (label === 'Tax') { player.money -= 100; this.bank += 100; this.log(`${player.name} paid 100$ tax.`); }
        if (label === 'Jail') { player.inJail = true; this.log(`${player.name} is in Jail. Wait one turn or click End Turn to skip.`); }
        if (label === 'GoToJail') { player.pos = 9; player.inJail = true; this.log(`${player.name} was sent to Jail!`); }
        if (label === 'Chance') { const r = Math.random(); if (r < 0.5) { player.money += 100; this.log(`${player.name} found 100$ (Chance).`); } else { player.money -= 50; this.log(`${player.name} lost 50$ (Chance).`) } }
        // mini-game redirects (open relevant mini-game page and pass player id)
        const mini = this.getMiniGameForIndex(s);
        if (mini) {
            // Forced entry: players must enter the mini-game. If they can't afford the minimum bet,
            // they play Russian Roulette (1 in 6 chance to survive and receive enough money to meet the min bet,
            // otherwise they are eliminated).
            if (player.money >= (this.MIN_BET || 10)) {
                this.save();
                // auto-redirect into mini-game
                setTimeout(() => { window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&fromMini=' + encodeURIComponent(mini) + '&advance=1'; }, 200);
                return;
            } else {
                // open an interactive Russian Roulette modal with a 1-in-6 spin
                this.openRussianRoulette(player, mini, label);
                return;
            }
        }
        // save and render, then check for game over
        this.save();
        this.renderPlayers();
        if (this.checkGameOver()) return;
        // automatically end the current player's turn after resolving non-redirect events
        // give a short delay so the player can see the result before the turn advances
        setTimeout(() => {
            // avoid ending turn if game is now over
            if (!this.gameOver) this.endTurn();
        }, 900);
    }

    showMiniGameConfirm(player, mini, label) {
        // ensure modal elements exist
        const modal = document.getElementById('miniConfirm');
        if (!modal) { this.log(`Opening ${mini}...`); this.save(); setTimeout(() => { window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&advance=1'; }, 350); return; }
        const title = document.getElementById('modalTitle');
        const body = document.getElementById('modalBody');
        const confirm = document.getElementById('modalConfirm');
        const cancel = document.getElementById('modalCancel');
        title.textContent = `Enter ${label}?`;
        body.textContent = `${player.name} landed on ${label}. Open the mini-game now?`;
        modal.setAttribute('aria-hidden', 'false');
        const onConfirm = () => {
            modal.setAttribute('aria-hidden', 'true');
            confirm.removeEventListener('click', onConfirm);
            cancel.removeEventListener('click', onCancel);
            this.save();
            // redirect and ask mini-game to return and auto-advance
            setTimeout(() => { window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&fromMini=' + encodeURIComponent(mini) + '&advance=1'; }, 200);
        };
        const onCancel = () => {
            modal.setAttribute('aria-hidden', 'true');
            confirm.removeEventListener('click', onConfirm);
            cancel.removeEventListener('click', onCancel);
            this.log(`${player.name} chose not to enter ${label}.`);
            // keep playing
        };
        confirm.addEventListener('click', onConfirm);
        cancel.addEventListener('click', onCancel);
    }

    // Open Russian Roulette modal — interactive 1-in-6 wheel spin
    openRussianRoulette(player, mini, label) {
        this.log(`${player.name} cannot afford the minimum bet (${this.MIN_BET}$). Russian Roulette initiated.`);
        const modal = document.getElementById('rrModal');
        const wheelRing = document.getElementById('rrWheelRing');
        const spinBtn = document.getElementById('rrSpin');
        const closeBtn = document.getElementById('rrClose');
        const msg = document.getElementById('rrMsg');
        if (!modal || !wheelRing || !spinBtn || !closeBtn || !msg) {
            // fallback immediate behavior
            const rr = Math.floor(Math.random() * 6) + 1;
            if (rr === 1) { player.money = this.MIN_BET; this.save(); this.renderPlayers(); setTimeout(() => { window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&fromMini=' + encodeURIComponent(mini) + '&advance=1'; }, 600); }
            else { const idx = this.players.findIndex(p => p.id === player.id); if (idx !== -1) this.players.splice(idx, 1); if (this.current >= this.players.length) this.current = 0; this.save(); this.renderPlayers(); if (this.players.length === 1) this.showWinner(this.players[0]); }
            return;
        }

        // show modal and reset visuals
        modal.setAttribute('aria-hidden', 'false');
        msg.textContent = '';
        spinBtn.disabled = false;

        // helper: show confetti briefly
        const showConfetti = () => {
            try {
                const conf = document.createElement('div'); conf.className = 'rr-confetti';
                modal.appendChild(conf);
                const emojis = ['🎉', '✨', '💥', '🌟', '🍀', '🎊'];
                for (let i = 0; i < 14; i++) {
                    const s = document.createElement('span'); s.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                    s.style.left = (30 + Math.random() * 120) + 'px';
                    s.style.top = (60 + Math.random() * 40) + 'px';
                    s.style.animationDelay = (Math.random() * 200) + 'ms';
                    conf.appendChild(s);
                }
                // remove after animation
                setTimeout(() => { conf.remove(); }, 1400);
            } catch (e) {/* ignore */ }
        };

        let spinning = false;
        const cleanup = () => {
            spinBtn.removeEventListener('click', onSpin);
            closeBtn.removeEventListener('click', onClose);
            wheelRing.removeEventListener('transitionend', onTransitionEnd);
            modal.setAttribute('aria-hidden', 'true');
        };

        const onClose = () => { if (spinning) return; cleanup(); this.log(`${player.name} cancelled Russian Roulette.`); };

        let chosenIndex = null;
        let transitionTimeout = null;
        const onTransitionEnd = (ev) => {
            // ensure we react once when the wheel finishes
            if (ev && ev.target !== wheelRing) return;
            // result handled in onSpin's timeout; nothing to do here but keep handler for robustness
        };

        const onSpin = () => {
            if (spinning) return;
            spinning = true;
            spinBtn.disabled = true;
            msg.textContent = 'Spinning...';

            // pick random segment 0..5 (0 is survive as per CSS gradient first segment)
            chosenIndex = Math.floor(Math.random() * 6);
            const spins = 3 + Math.floor(Math.random() * 3); // 3..5
            const segmentCenter = chosenIndex * 60 + 30; // degrees
            const currentRot = parseFloat(wheelRing.dataset.rot || '0');
            const targetRot = currentRot + (360 * spins) - segmentCenter;
            const duration = 1400 + spins * 300; // ms
            // apply transform
            wheelRing.style.transition = `transform ${duration}ms cubic-bezier(.2,.7,.2,1)`;
            wheelRing.style.transform = `rotate(${targetRot}deg)`;
            wheelRing.dataset.rot = targetRot;

            // safety timeout if transitionend doesn't fire reliably
            if (transitionTimeout) clearTimeout(transitionTimeout);
            transitionTimeout = setTimeout(() => {
                // outcome: survive if chosenIndex === 0
                const outcome = chosenIndex + 1;
                if (chosenIndex === 0) {
                    msg.textContent = `Survived! You receive $${this.MIN_BET} and may enter ${label}.`;
                    showConfetti();
                    player.money = this.MIN_BET;
                    this.save();
                    this.renderPlayers();
                    setTimeout(() => { cleanup(); window.location.href = mini + '?player=' + encodeURIComponent(player.id) + '&return=board&fromMini=' + encodeURIComponent(mini) + '&advance=1'; }, 900);
                } else {
                    msg.textContent = `You lost (rolled ${outcome}). You are eliminated.`;
                    const idx = this.players.findIndex(p => p.id === player.id);
                    if (idx !== -1) this.players.splice(idx, 1);
                    if (this.current >= this.players.length) this.current = 0;
                    this.save();
                    this.renderPlayers();
                    setTimeout(() => { cleanup(); if (this.players.length === 1) this.showWinner(this.players[0]); }, 900);
                }
                spinning = false;
            }, duration + 80);
        };

        spinBtn.addEventListener('click', onSpin);
        closeBtn.addEventListener('click', onClose);
        wheelRing.addEventListener('transitionend', onTransitionEnd);
    }

    // return mini-game page for a given perimeter index (or null)
    getMiniGameForIndex(i) {
        // map specific indices to mini-games (adjustable)
        // spread casino tiles around the board so landing can open a mini-game
        const map = {
            // Blackjack tables
            6: 'black-jack.html',
            16: 'black-jack.html',
            24: 'black-jack.html',
            // Slots
            3: 'slots.html',
            9: 'slots.html',
            26: 'slots.html',
            31: 'slots.html',
            // Roulette
            11: 'roulette.html',
            19: 'roulette.html',
            36: 'roulette.html',
            // Baccarat
            14: 'backarat.html',
            38: 'backarat.html',
            // Chance / small events
            2: 'chance.html',
            17: 'chance.html',
            33: 'chance.html'
        };
        return map[i] || null;
    }

    endTurn() {
        // clear jail if they served a turn
        const player = this.players[this.current];
        if (player && player.inJail) { player.inJail = false; this.log(`${player.name} is released from jail.`); }
        this.current = (this.current + 1) % Math.max(1, this.players.length);
        this.save();
        this.updateStatus();
        this.log(`Turn: ${this.players[this.current].name}`);

        // Trigger the popup
        this.announceTurn();
    }

    // Popup logic
    announceTurn() {
        if (this.players.length === 0) return;
        const player = this.players[this.current];
        const announcer = document.getElementById('turnAnnouncer');
        const iconEl = document.getElementById('turnIcon');
        const nameEl = document.getElementById('turnName');

        if (!announcer) return;

        iconEl.textContent = player.icon || '🎲';
        nameEl.textContent = `${player.name}'s Turn!`;

        announcer.classList.add('show');
        setTimeout(() => {
            announcer.classList.remove('show');
        }, 1800); // Pops up and fades away after 1.8 seconds
    }

    log(msg) {
        const time = new Date().toLocaleTimeString();
        const line = document.createElement('div'); line.textContent = `[${time}] ${msg}`;
        this.logEl.prepend(line);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // ensure js folder exists in repo; instantiate game
    const g = new Game();
    // expose to console for debugging
    window.GamBoard = g;
});