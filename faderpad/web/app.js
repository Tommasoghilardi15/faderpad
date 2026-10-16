/* Faderpad web app. Plain JavaScript, no build step. */
(() => {
  'use strict';

  /* ---------- translations ---------- */

  const STRINGS = {
    en: {
      connecting: 'Connecting…',
      general: 'General',
      generalSub: 'Channel volume',
      mixVolume: 'Mix volume',
      mixMaster: 'mix volume',
      muted: 'Muted',
      mute: 'Mute',
      unmute: 'Unmute',
      wavelinkDown: 'Wave Link isn\u2019t responding',
      wavelinkDownHint: 'Open Wave Link on the PC. Faderpad reconnects by itself.',
      pcDown: 'Can\u2019t reach the PC',
      pcDownHint: 'Check that Faderpad is running on the PC and that this device is on the same network.',
      media: 'Media',
      mediaKeysHint: 'Controls the app Windows is playing',
      nothingPlaying: 'Nothing playing',
      previous: 'Previous track',
      next: 'Next track',
      play: 'Play',
      pause: 'Pause',
      pinTitle: 'Enter PIN',
      pinHint: 'Faderpad on this PC is protected by a PIN.',
      pinButton: 'Unlock',
      wrongPin: 'Wrong PIN. Try again.',
    },
    it: {
      connecting: 'Collegamento…',
      general: 'Generale',
      generalSub: 'Volume del canale',
      mixVolume: 'Volume del mix',
      mixMaster: 'volume del mix',
      muted: 'Muto',
      mute: 'Silenzia',
      unmute: 'Riattiva',
      wavelinkDown: 'Wave Link non risponde',
      wavelinkDownHint: 'Apri Wave Link sul PC: Faderpad si ricollega da solo.',
      pcDown: 'PC non raggiungibile',
      pcDownHint: 'Controlla che Faderpad sia acceso sul PC e che questo dispositivo sia sulla stessa rete.',
      media: 'Media',
      mediaKeysHint: 'Comanda l\u2019app che Windows sta riproducendo',
      nothingPlaying: 'Niente in riproduzione',
      previous: 'Brano precedente',
      next: 'Brano successivo',
      play: 'Riproduci',
      pause: 'Pausa',
      pinTitle: 'Inserisci il PIN',
      pinHint: 'Faderpad su questo PC è protetto da un PIN.',
      pinButton: 'Sblocca',
      wrongPin: 'PIN sbagliato. Riprova.',
    },
  };
  const LANG = (navigator.language || 'en').toLowerCase().startsWith('it') ? 'it' : 'en';
  const T = STRINGS[LANG];
  document.documentElement.lang = LANG;
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = T[el.dataset.i18n]; });
  document.querySelectorAll('[data-i18n-label]').forEach(el => el.setAttribute('aria-label', T[el.dataset.i18nLabel]));

  /* ---------- icons ---------- */

  const svg = (d, filled) =>
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="' + (filled ? 'currentColor' : 'none') +
    '" stroke="' + (filled ? 'none' : 'currentColor') +
    '" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' + d + '</svg>';

  const ICON = {
    mic: svg('<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21M8.5 21h7"/>'),
    music: svg('<path d="M9 18V5.5l10-2V16"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>'),
    browser: svg('<rect x="3" y="4.5" width="18" height="15" rx="2.5"/><path d="M3 9h18"/><path d="M6.5 6.8h.01M9 6.8h.01"/>'),
    chat: svg('<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 3.5V16h0a2.5 2.5 0 0 1-1.5-2.3z"/><path d="M8.5 10h.01M12 10h.01M15.5 10h.01"/>'),
    game: svg('<path d="M7.5 7.5h9a4.5 4.5 0 0 1 4.5 4.5v1.8a3 3 0 0 1-5.3 1.9L14.4 14H9.6l-1.3 1.7A3 3 0 0 1 3 13.8V12a4.5 4.5 0 0 1 4.5-4.5z"/><path d="M8 10v3.5M6.25 11.75h3.5M15.5 11h.01M17.5 13h.01"/>'),
    wave: svg('<path d="M3 12h2.5l2-5 3.5 10 3-12 3 9 1.5-2H21"/>'),
    headphones: svg('<path d="M4 15v-2.5a8 8 0 0 1 16 0V15"/><rect x="3" y="14" width="4.5" height="6.5" rx="1.6"/><rect x="16.5" y="14" width="4.5" height="6.5" rx="1.6"/>'),
    speaker: svg('<rect x="5.5" y="3" width="13" height="18" rx="2.5"/><circle cx="12" cy="14.2" r="3.3"/><path d="M12 7.3h.01"/>'),
    broadcast: svg('<circle cx="12" cy="12" r="1.8"/><path d="M8.3 8.3a5.2 5.2 0 0 0 0 7.4M15.7 8.3a5.2 5.2 0 0 1 0 7.4M5.4 5.4a9.3 9.3 0 0 0 0 13.2M18.6 5.4a9.3 9.3 0 0 1 0 13.2"/>'),
    volume: svg('<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>'),
    muted: svg('<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M16 9.5l5 5M21 9.5l-5 5"/>'),
    previous: svg('<path d="M6 5h2.2v14H6zM19.5 5.6v12.8L9.6 12z"/>', true),
    next: svg('<path d="M15.8 5H18v14h-2.2zM4.5 5.6v12.8l9.9-6.4z"/>', true),
    play: svg('<path d="M7.5 4.8v14.4L19 12z"/>', true),
    pause: svg('<path d="M6.5 5h4v14h-4zM13.5 5h4v14h-4z"/>', true),
  };

  const $ = id => document.getElementById(id);
  const div = cls => { const el = document.createElement('div'); el.className = cls; return el; };

  /* ---------- state ---------- */

  let state = null;                   // last snapshot from Wave Link
  let media = null;                   // last media snapshot
  let icons = {channels: {}, mixes: {}};
  let levels = {c: {}, m: {}};        // live amplitudes 0..1
  let layoutKey = '';
  let started = false;
  const controls = new Map();         // key -> cell with a fader
  const tiles = [];                   // icon tiles to refresh when real icons arrive
  const lastTouch = new Map();        // key -> time of the last local change

  /* ---------- names and icons ---------- */

  // "FortniteClient-Win64-Shipping" -> "Fortnite"
  function prettyName(name) {
    return (name || '').replace(/-Win64-Shipping$/i, '').replace(/Client$/, '') || name;
  }
  function channelKind(c) {
    const n = (c.name || '').toLowerCase();
    if ((c.type || '').toLowerCase() === 'hardware' || /micro|\bmic\b|wave:|voice|voce/.test(n)) return 'mic';
    if (/spotify|music|musica|deezer|tidal|itunes|apple music|soundcloud|youtube music/.test(n)) return 'music';
    if (/chrome|edge|firefox|opera|brave|safari|browser|vivaldi|arc/.test(n)) return 'browser';
    if (/discord|teams|zoom|skype|telegram|whatsapp|slack|chat/.test(n)) return 'chat';
    if (/game|gioco|shipping|win64|steam|epic|fortnite|valorant|minecraft|rainbow|league|cs2|apex|overwatch/.test(n)) return 'game';
    return 'wave';
  }
  function mixKind(m) {
    const n = (m.name || '').toLowerCase();
    if (/speaker|cass|altoparlant|monitor speaker/.test(n)) return 'speaker';
    if (/personal|headphone|headset|cuffie|monitor/.test(n)) return 'headphones';
    if (/stream|chat|broadcast|live|record|diretta/.test(n)) return 'broadcast';
    return 'wave';
  }
  function fillTile(tile, src, kind) {
    tile.className = tile.className.replace(/\bt-\w+/g, '').replace(/\bhas-image\b/, '').trim() + ' t-' + kind;
    if (src) {
      const img = new Image();
      img.alt = '';
      img.onerror = () => { tile.classList.remove('has-image'); tile.innerHTML = ICON[kind]; };
      img.src = src;
      tile.innerHTML = '';
      tile.classList.add('has-image');
      tile.append(img);
    } else {
      tile.innerHTML = ICON[kind];
    }
  }
  function makeTile(group, id, kind) {
    const tile = div('tile');
    tiles.push({tile, group, id, kind});
    fillTile(tile, icons[group][id], kind);
    return tile;
  }
  function refreshIcons() {
    for (const t of tiles) fillTile(t.tile, icons[t.group][t.id], t.kind);
  }

  /* ---------- talking to the PC ---------- */

  function showStatus(kind, text, notice) {
    const el = $('status');
    el.className = 'status ' + kind;
    el.querySelector('span').textContent = text;
    $('notice').textContent = notice || '';
  }
  function pcUnreachable() {
    showStatus('error', T.pcDown, T.pcDownHint);
  }
  function handleUnauthorized(response) {
    if (response.status === 401) { showPinScreen(); throw new Error('pin_required'); }
    return response;
  }
  function post(url, body) {
    return fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
      .then(handleUnauthorized)
      .then(r => r.json());
  }

  // One request at a time per control: values that arrive while one is in flight
  // are merged and only the latest is sent, so faders stay smooth.
  const queues = new Map();
  function send(key, body) {
    let q = queues.get(key);
    if (!q) { q = {busy: false, next: null}; queues.set(key, q); }
    if (q.busy) { q.next = body; return; }
    q.busy = true;
    post('/api/set', body)
      .then(d => { if (d.error) showStatus('error', T.wavelinkDown, T.wavelinkDownHint); })
      .catch(e => { if (e.message !== 'pin_required') pcUnreachable(); })
      .finally(() => {
        q.busy = false;
        if (q.next) { const n = q.next; q.next = null; send(key, n); }
      });
  }

  /* ---------- fader ---------- */

  function makeFader(ariaLabel, onChange) {
    const el = div('fader');
    el.tabIndex = 0;
    el.setAttribute('role', 'slider');
    el.setAttribute('aria-label', ariaLabel);
    el.setAttribute('aria-valuemin', '0');
    el.setAttribute('aria-valuemax', '100');
    el.innerHTML = '<div class="track"><div class="fill"></div><div class="meter"></div></div><div class="thumb"></div>';
    const f = {el, value: 0, dragging: false, meter: el.querySelector('.meter'), clip: ''};
    f.set = v => {
      f.value = Math.min(1, Math.max(0, v));
      el.style.setProperty('--v', f.value);
      el.setAttribute('aria-valuenow', String(Math.round(f.value * 100)));
    };

    // A tap jumps to the touched spot; a drag moves relative to where the thumb was.
    let grab = null;
    el.addEventListener('pointerdown', e => {
      if (e.button > 0) return;
      grab = {id: e.pointerId, x: e.clientX, v: f.value, moved: false};
      el.setPointerCapture(e.pointerId);
    });
    el.addEventListener('pointermove', e => {
      if (!grab || e.pointerId !== grab.id) return;
      const dx = e.clientX - grab.x;
      if (!grab.moved && Math.abs(dx) < 4) return;
      grab.moved = true;
      f.dragging = true;
      el.classList.add('dragging');
      f.set(grab.v + dx / Math.max(1, el.clientWidth - 26));
      onChange(f.value);
    });
    const release = (e, cancelled) => {
      if (!grab || e.pointerId !== grab.id) return;
      if (!grab.moved && !cancelled) {
        const r = el.getBoundingClientRect();
        f.set((e.clientX - r.left - 13) / Math.max(1, r.width - 26));
        onChange(f.value);
      } else if (grab.moved) {
        onChange(f.value);
      }
      grab = null;
      f.dragging = false;
      el.classList.remove('dragging');
    };
    el.addEventListener('pointerup', e => release(e, false));
    el.addEventListener('pointercancel', e => release(e, true));
    el.addEventListener('keydown', e => {
      const steps = {ArrowRight: 0.01, ArrowUp: 0.01, ArrowLeft: -0.01, ArrowDown: -0.01, PageUp: 0.1, PageDown: -0.1};
      let v = null;
      if (e.key in steps) v = f.value + steps[e.key] * (e.shiftKey ? 5 : 1);
      if (e.key === 'Home') v = 0;
      if (e.key === 'End') v = 1;
      if (v === null) return;
      e.preventDefault();
      f.set(v);
      onChange(f.value);
    });
    return f;
  }

  /* ---------- cells ---------- */

  // o: {key, ariaLabel, label, read(), body(change), amplitude(cell), title?}
  function makeCell(o) {
    const el = div('cell');
    const cell = {o, el, level: 0, muted: false, shown: 0};

    if (o.title) {
      const t = div('mix-title');
      const texts = document.createElement('div');
      texts.innerHTML = '<strong></strong><small></small>';
      texts.querySelector('strong').textContent = o.title.name;
      cell.sub = texts.querySelector('small');
      t.append(o.title.tile, texts);
      el.append(t);
    }

    cell.button = document.createElement('button');
    cell.button.className = 'mute';
    cell.button.addEventListener('click', () => {
      cell.muted = !cell.muted;
      lastTouch.set(o.key, Date.now());
      paint(cell);
      send(o.key + ':muted', o.body({muted: cell.muted}));
    });

    const label = div('label');
    label.textContent = o.label;

    cell.value = div('value');
    cell.fader = makeFader(o.ariaLabel, v => {
      cell.level = v;
      lastTouch.set(o.key, Date.now());
      cell.value.textContent = Math.round(v * 100);
      send(o.key, o.body({level: Math.round(v * 1000) / 1000}));
    });

    el.append(cell.button, label, cell.fader.el, cell.value);
    controls.set(o.key, cell);
    return el;
  }

  function paint(cell) {
    cell.el.classList.toggle('is-muted', cell.muted);
    cell.button.innerHTML = cell.muted ? ICON.muted : ICON.volume;
    cell.button.setAttribute('aria-pressed', String(cell.muted));
    cell.button.setAttribute('aria-label', (cell.muted ? T.unmute : T.mute) + ': ' + cell.o.ariaLabel);
    if (cell.sub) cell.sub.textContent = cell.muted ? T.muted : T.mixVolume;
    if (!cell.fader.dragging) {
      cell.fader.set(cell.level);
      cell.value.textContent = Math.round(cell.level * 100);
    }
  }

  /* ---------- building the grid ---------- */

  function layoutOf(s) {
    return JSON.stringify([
      s.mixes.map(m => [m.id, m.name]),
      s.channels.map(c => [c.id, c.name, c.type, Object.keys(c.mixes).sort()]),
    ]);
  }
  const channelById = id => state.channels.find(c => c.id === id);
  const mixById = id => state.mixes.find(m => m.id === id);

  function build() {
    const grid = $('grid');
    grid.innerHTML = '';
    controls.clear();
    tiles.length = 0;
    grid.style.setProperty('--columns', String(1 + state.mixes.length));

    // Header: empty corner, "General", then one column per mix with its master volume.
    const header = div('row mix-row');
    const general = div('general-head');
    general.innerHTML = '<strong></strong><small></small>';
    general.querySelector('strong').textContent = T.general;
    general.querySelector('small').textContent = T.generalSub;
    header.append(div('corner'), general);
    for (const m of state.mixes) {
      header.append(makeCell({
        key: 'mix|' + m.id,
        ariaLabel: m.name + ', ' + T.mixMaster,
        label: m.name,
        title: {name: m.name, tile: makeTile('mixes', m.id, mixKind(m))},
        read: () => mixById(m.id),
        body: x => ({kind: 'mix', mix: m.id, ...x}),
        amplitude: cell => cell.muted ? 0 : (levels.m[m.id] || 0),
      }));
    }
    grid.append(header);

    // One row per channel.
    for (const ch of state.channels) {
      const row = div('row');
      const head = div('head');
      const name = div('name');
      name.textContent = prettyName(ch.name);
      name.title = ch.name;
      head.append(makeTile('channels', ch.id, channelKind(ch)), name);
      row.append(head);

      row.append(makeCell({
        key: 'channel|' + ch.id,
        ariaLabel: prettyName(ch.name) + ', ' + T.general,
        label: T.general,
        read: () => channelById(ch.id),
        body: x => ({kind: 'channel', channel: ch.id, ...x}),
        amplitude: cell => cell.muted ? 0 : (levels.c[ch.id] || 0),
      }));

      for (const m of state.mixes) {
        if (!ch.mixes[m.id]) { row.append(div('cell empty')); continue; }
        row.append(makeCell({
          key: 'channel|' + ch.id + '|' + m.id,
          ariaLabel: prettyName(ch.name) + ', ' + m.name,
          label: m.name,
          read: () => { const c = channelById(ch.id); return c && c.mixes[m.id]; },
          body: x => ({kind: 'channel', channel: ch.id, mix: m.id, ...x}),
          amplitude: cell => {
            const c = channelById(ch.id);
            if (cell.muted || !c || c.muted) return 0;
            return levels.c[ch.id] || 0;
          },
        }));
      }
      grid.append(row);
    }

    fetch('/api/icons').then(handleUnauthorized).then(r => r.json()).then(d => {
      if (!d.error) { icons = {channels: d.channels || {}, mixes: d.mixes || {}}; refreshIcons(); }
    }).catch(() => {});
  }

  function render() {
    const key = layoutOf(state);
    if (key !== layoutKey) { layoutKey = key; build(); }
    const now = Date.now();
    for (const cell of controls.values()) {
      if (now - (lastTouch.get(cell.o.key) || 0) < 900) continue;  // just changed here
      const s = cell.o.read();
      if (!s) continue;
      cell.level = s.level ?? 0;
      cell.muted = !!s.muted;
      paint(cell);
    }
  }

  function refresh() {
    if ([...controls.values()].some(c => c.fader.dragging)) return;
    fetch('/api/state').then(handleUnauthorized).then(r => r.json()).then(d => {
      media = d.media;
      renderMedia();
      if (!d.wavelink) {
        showStatus('error', T.wavelinkDown, T.wavelinkDownHint);
        return;
      }
      state = d.wavelink;
      const v = state.version ? ' ' + state.version.split('.').slice(0, 2).join('.') : '';
      showStatus('ok', 'Wave Link' + v, '');
      render();
    }).catch(e => { if (e.message !== 'pin_required') pcUnreachable(); });
  }

  /* ---------- live level meters ---------- */

  // Wave Link sends amplitudes 0..1. Show them on a -60..0 dB scale like a real meter,
  // scaled to the fader position: after the fader, the signal can't go past the thumb.
  function toMeter(a) {
    if (!(a > 0)) return 0;
    return Math.min(1, Math.max(0, (20 * Math.log10(a) + 60) / 60));
  }
  function animate() {
    for (const cell of controls.values()) {
      const target = toMeter(cell.o.amplitude(cell)) * cell.fader.value;
      cell.shown = target >= cell.shown ? target : cell.shown * 0.86 + target * 0.14;
      if (cell.shown < 0.005) cell.shown = 0;
      const clip = 'inset(0 ' + (100 - cell.shown * 100).toFixed(1) + '% 0 0)';
      if (clip !== cell.fader.clip) { cell.fader.clip = clip; cell.fader.meter.style.clipPath = clip; }
    }
    requestAnimationFrame(animate);
  }
  function openLevels() {
    const source = new EventSource('/api/levels');
    source.onmessage = e => { try { levels = JSON.parse(e.data); } catch (_) { /* ignore */ } };
    source.onerror = () => { levels = {c: {}, m: {}}; };
  }

  /* ---------- media players ---------- */

  // One card per app Windows sees playing or paused (Spotify, a Twitch tab, YouTube…).
  // Cards keep Windows' order, so pausing one doesn't move the buttons under your finger.
  const players = new Map();   // session id -> card
  let playersKey = '';

  function makePlayer(id) {
    const el = div('player');
    el.innerHTML =
      '<div class="cover t-music"></div>' +
      '<div class="track-info"><small></small><span></span></div>' +
      '<div class="transport"><button></button><button class="primary"></button><button></button></div>';
    const [previous, playPause, next] = el.querySelectorAll('button');
    const card = {
      id, el, session: null, coverSrc: undefined,
      cover: el.querySelector('.cover'), sub: el.querySelector('small'), title: el.querySelector('span'),
      previous, playPause, next,
    };
    previous.innerHTML = ICON.previous;
    next.innerHTML = ICON.next;
    previous.setAttribute('aria-label', T.previous);
    next.setAttribute('aria-label', T.next);
    previous.addEventListener('click', () => mediaCommand(card, 'previous'));
    playPause.addEventListener('click', () => mediaCommand(card, 'play_pause'));
    next.addEventListener('click', () => mediaCommand(card, 'next'));
    return card;
  }

  function paintPlayer(card, s) {
    card.session = s;
    const keysOnly = media.backend === 'keys';
    card.title.textContent = keysOnly ? T.media : (s.title || T.nothingPlaying);
    card.sub.textContent = keysOnly ? T.mediaKeysHint : [s.artist, s.app].filter(Boolean).join(' \u2013 ');

    const playing = s.playing === true;
    card.playPause.innerHTML = playing ? ICON.pause : ICON.play;
    card.playPause.setAttribute('aria-label', (playing ? T.pause : T.play) + (s.app ? ': ' + s.app : ''));
    card.playPause.disabled = s.can_play_pause === false;
    card.previous.disabled = s.can_previous === false;
    card.next.disabled = s.can_next === false;

    if (s.cover !== card.coverSrc) {
      card.coverSrc = s.cover;
      if (s.cover) {
        const img = new Image();
        img.alt = '';
        img.onerror = () => { card.cover.innerHTML = ICON.music; };
        img.src = s.cover;
        card.cover.innerHTML = '';
        card.cover.append(img);
      } else {
        card.cover.innerHTML = ICON.music;
      }
    }
  }

  function renderMedia() {
    const box = $('players');
    const sessions = media && media.available ? (media.sessions || []) : [];
    box.hidden = sessions.length === 0;
    box.classList.toggle('several', sessions.length > 1);
    box.classList.toggle('many', sessions.length > 2);

    const key = sessions.map(s => s.id).join('|');
    if (key !== playersKey) {
      playersKey = key;
      box.innerHTML = '';
      const old = new Map(players);
      players.clear();
      for (const s of sessions) {
        const card = old.get(s.id) || makePlayer(s.id);
        players.set(s.id, card);
        box.append(card.el);
      }
    }
    for (const s of sessions) paintPlayer(players.get(s.id), s);
  }

  function mediaCommand(card, action) {
    const s = card.session;
    if (action === 'play_pause' && s && s.playing !== null) {
      s.playing = !s.playing;   // feels instant; the next refresh confirms
      paintPlayer(card, s);
    }
    post('/api/media', {action, session: card.id})
      .catch(e => { if (e.message !== 'pin_required') pcUnreachable(); })
      .then(() => setTimeout(refresh, 600));
  }

  /* ---------- PIN ---------- */

  function showPinScreen() {
    $('pin-screen').hidden = false;
    setTimeout(() => $('pin-input').focus(), 50);
  }
  $('pin-form').addEventListener('submit', e => {
    e.preventDefault();
    $('pin-error').textContent = '';
    fetch('/api/auth', {method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({pin: $('pin-input').value})})
      .then(r => {
        if (!r.ok) throw new Error('wrong');
        $('pin-screen').hidden = true;
        $('pin-input').value = '';
        start();
      })
      .catch(() => { $('pin-error').textContent = T.wrongPin; $('pin-input').select(); });
  });

  /* ---------- start ---------- */

  function start() {
    if (started) { refresh(); return; }
    started = true;
    refresh();
    setInterval(refresh, 1500);
    openLevels();
    requestAnimationFrame(animate);
  }

  fetch('/api/info').then(r => r.json()).then(info => {
    if (info.pin_required && !info.authorized) showPinScreen();
    else start();
  }).catch(pcUnreachable);
})();
