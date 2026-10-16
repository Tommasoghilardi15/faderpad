<p align="center">
  <img src="assets/icon.png" width="96" height="96" alt="">
</p>

<h1 align="center">Faderpad</h1>

<p align="center">
  Control Elgato Wave Link from your tablet or phone.<br>
  <a href="../../releases/latest"><strong>Download for Windows</strong></a> · <a href="README.it.md">Italiano</a>
</p>

<p align="center">
  <img src="docs/screenshot-dark.png" alt="Faderpad on a tablet: Wave Link channels as rows, mixes as columns, a media player at the bottom">
</p>

Faderpad turns any tablet or phone into a touch mixer for Wave Link 3. It shows the same grid as Wave Link, with your channels, your mixes and live level meters, so you can turn the music down or mute a call without leaving your game.

> Faderpad is an independent open-source project. It is not made, endorsed or supported by Elgato.

## Features

- **Your setup, whatever it is.** Channels and mixes are read from Wave Link every time, so Faderpad shows exactly what you have configured.
- **Every fader.** The volume of each channel, of each channel inside each mix, and of each mix as a whole. Mute any of them with one tap.
- **Live level meters** inside the faders, like in Wave Link.
- **Media controls for whatever is playing**: Spotify, a Twitch or YouTube tab, Apple Music, VLC and any app Windows knows about, with title, artist and cover. Several apps at once each get their own card.
- **Runs in the browser.** iPad, Android tablet, phone or another computer. Add it to the Home Screen and it opens full screen, like an app.
- **Quick to connect.** On start, the PC shows a QR code to scan with the tablet.
- **Optional PIN**, so other people on your network can't change your volumes.
- Light and dark theme from your device settings. English and Italian.

## Requirements

- Windows 10 or 11 with [Elgato Wave Link](https://www.elgato.com/wave-link) 3 open
- A tablet or phone on the same network as the PC

## Get started

1. Download **Faderpad.exe** from the [latest release](../../releases/latest).
2. Open Wave Link, then double-click Faderpad.exe.
3. The first time, Windows Firewall asks whether Faderpad may use the network. Allow it on private networks.
4. A page with a QR code opens on the PC. Scan it with your tablet, or type the address it shows.

Keep Faderpad's window open while you use it; close the window to stop it.

Faderpad.exe isn't code-signed, so Windows SmartScreen may warn you the first time. Choose **More info**, then **Run anyway**.

<p align="center">
  <img src="docs/connect.png" width="600" alt="The connection page with a QR code and the address to open">
</p>

## Settings

Put a file named `faderpad.json` next to Faderpad.exe (there is an example in [`faderpad.example.json`](faderpad.example.json)):

```json
{
  "port": 5757,
  "pin": "1234",
  "open_browser": true
}
```

| Setting | Default | What it does |
| --- | --- | --- |
| `port` | `5757` | The port the tablet connects to. Change it if something else already uses 5757. |
| `pin` | none | Other devices must enter this PIN once before they can control anything. The PC itself never needs it. |
| `open_browser` | `true` | Open the QR code page on the PC when Faderpad starts. |

The same options work on the command line: `Faderpad.exe --port 6000 --pin 1234 --no-browser`. Run `Faderpad.exe --help` for the full list.

## How it works

```
Tablet browser  <-- your network -->  Faderpad on the PC  <-- local API -->  Wave Link
                                              |
                                              +-- Windows media controls
```

Faderpad is a small web server running on your PC. It talks to Wave Link through the local API Wave Link opens for apps like the Stream Deck plugin, using the [wavelink-adapter](https://github.com/Nekit678/WaveLinkAdapter) library. Now-playing information and the play, previous and next buttons go through the Windows system media controls.

Everything stays on your network: no account, no cloud, no data sent anywhere.

## Troubleshooting

**"Wave Link isn't responding"** Open Wave Link on the PC. Faderpad reconnects on its own.

**The tablet can't open the page.** Check that it is on the same network as the PC; guest Wi-Fi networks usually keep devices apart. Make sure Faderpad is allowed in Windows Firewall (*Windows Security → Firewall & network protection → Allow an app through firewall*).

**There are no media cards.** They appear when an app is playing or paused. Start something in Spotify or in the browser.

**My antivirus flags Faderpad.exe.** Programs packaged with PyInstaller are sometimes flagged by mistake. You can check the code here and [build the .exe yourself](#build-the-exe), or [run it from source](#run-from-source).

**Something else.** Open `http://localhost:5757/api/debug` on the PC: it shows what Faderpad sees from Wave Link and from the media controls. Include it when you open an issue.

## Run from source

You need Python 3.11 or newer.

```bash
git clone https://github.com/tommasoghilardi15/faderpad.git
cd faderpad
python -m pip install -r requirements.txt
python -m faderpad
```

## Build the .exe

- **On your PC:** double-click `build_exe.bat`. The result is `dist\Faderpad.exe`.
- **On GitHub:** every push builds the .exe (you'll find it under *Actions*). Pushing a version tag such as `v1.0.1` also publishes a release with the .exe attached.

## Project layout

```
faderpad/
  __main__.py     command line, settings, startup
  server.py       web server and JSON API
  wavelink.py     everything that talks to Wave Link
  media.py        Windows media controls
  web/            the web app (HTML, CSS, JavaScript, no build step)
faderpad.spec     PyInstaller recipe for the .exe
```

## Contributing

Issues and pull requests are welcome. Some ideas for what could come next: hiding or reordering channels from the page, more languages, vertical faders for phones.

## Credits

- [wavelink-adapter](https://github.com/Nekit678/WaveLinkAdapter) by Nekit678 (MIT), the client for Wave Link's local API
- [Flask](https://flask.palletsprojects.com/), [qrcode](https://github.com/lincolnloop/python-qrcode) and [PyWinRT](https://github.com/pywinrt/pywinrt)

## License

[MIT](LICENSE) © 2026 Tommaso Ghilardi. Use it, change it, share it.

Elgato and Wave Link are trademarks of their respective owners.
