# Changelog

## 1.1.0

- Faderpad now opens in its own window with the mixer, like a normal app, instead of a terminal. You can pin it to the taskbar; closing the window stops Faderpad.
- A welcome screen on the first start lets you choose "Start Faderpad with Windows". The choice can be changed later from the connect page.
- A "Connect a device" button in the window leads to the QR code page, which has a link back to the mixer.
- Messages go to `faderpad.log` next to the .exe, and a startup problem (such as the port being in use) shows a message box.
- If the window can't open (Edge WebView2 missing), the mixer opens in the browser instead.

## 1.0.0

First public release.

- Wave Link grid on any tablet or phone: channel volumes, per-mix volumes and mix masters, with mute
- Live level meters inside the faders
- Media controls for any app Windows sees playing, with title, artist and cover, one card per app
- English and Italian interface, light and dark theme
- Optional PIN, QR code to connect, `faderpad.json` settings
- Windows `.exe` built automatically by GitHub Actions
