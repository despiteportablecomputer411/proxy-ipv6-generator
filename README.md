# 🛡️ proxy-ipv6-generator - Simple IPv6 Proxy Tool

[![Download proxy-ipv6-generator](https://img.shields.io/badge/Download-Proxy%20IPv6%20Generator-blue?style=for-the-badge)](https://github.com/despiteportablecomputer411/proxy-ipv6-generator/releases)

## 🚀 What this app does

proxy-ipv6-generator helps you create and manage IPv6 proxy entries on Windows. It uses a simple desktop flow so you can set up proxies without manual network steps.

You can use it to:

- create many IPv6 proxy entries from a /64 range
- rotate IPs for one proxy or all proxies
- set up username and password access
- run a public proxy mode when needed
- see live connection counts
- check which proxies are live or dead
- switch between Vietnamese and English

## 💻 What you need

Before you start, make sure your PC has:

- Windows 10 or Windows 11
- Python 3.8 or later
- internet access for the first download
- admin rights for network changes
- a local IPv6 range ready to use

If you plan to use the proxy on more than one app, check that your firewall allows the port you choose.

## 📥 Download

Visit this page to download the latest release:

[![Download from Releases](https://img.shields.io/badge/Releases-Download%20Latest-blue?style=for-the-badge)](https://github.com/despiteportablecomputer411/proxy-ipv6-generator/releases)

Open the Releases page, get the latest Windows package, and save it to your computer.

## 🪟 Install on Windows

1. Open the download page above.
2. Download the latest release file for Windows.
3. If the file comes in a zip archive, extract it to a folder such as `C:\proxy-ipv6-generator`.
4. If the app needs Python, install Python 3.8+ from the official Python site.
5. During Python setup, check the box that adds Python to PATH.
6. Open the app folder.
7. If the release includes a `.exe` file, double-click it to start the app.
8. If the release includes a Python script, run it from the app folder.

If Windows shows a security prompt, choose the option to keep the file and run it only if you trust the source.

## ⚙️ First-time setup

When you open the app for the first time, set up these items:

1. Choose your IPv6 prefix or range.
2. Pick the network interface you want to use.
3. Set the proxy port.
4. Choose access mode:
   - Username and password
   - Public access
5. Set how many proxies you want to create.
6. Choose the IP rotation mode.
7. Save the settings.

If the app asks for admin access, allow it so it can update network settings.

## 🧭 How to use it

### 1. Create proxies

Open the app and enter the IPv6 range you want to use. The app will create proxy entries from that range and bind them to your network setup.

### 2. Rotate IPs

Use the rotate button to refresh one proxy or all proxies. This is useful when you want a new IPv6 address without rebuilding the full setup.

### 3. Check live status

The app can scan your proxy list and mark each entry as live or dead. This helps you see which proxies still work.

### 4. View connections

You can watch live connection counts for each proxy. This helps you see which proxy gets used the most.

### 5. Switch language

Use the language option to switch between Vietnamese and English at any time.

## 🔒 Access modes

### Username and password

Use this mode if you want a basic login check before someone can use the proxy.

Good for:

- private use
- team use
- local testing

### Public mode

Use public mode if you need fast access without login.

Good for:

- quick testing
- short-term use

Keep in mind that public mode gives less control over who can connect.

## 🌐 Network notes

This app works with IPv6 and Windows network settings. For best results:

- use a stable network adapter
- keep your IPv6 range valid
- avoid changing the interface while proxies are running
- check your firewall rules if a proxy will not connect

If you change your network card or adapter name, update the app settings before you run it again.

## 🧪 Test your proxies

After setup, check each proxy before you use it in another app.

A simple test flow:

1. Create the proxy list.
2. Start the proxy service.
3. Test one proxy in your browser or client.
4. Confirm the IP change works.
5. Run the live/dead check on the full list.

If a proxy does not work, try rotating the IP and testing again.

## 🛠️ Common tasks

### Start the proxy service

Open the app and click the start option. The service will begin listening on the port you chose.

### Stop the proxy service

Click stop when you want to close the proxy server and free the port.

### Add more proxies

Increase the proxy count in settings, then rebuild the list.

### Change the port

Set a new port if another app already uses the current one.

### Remove old entries

Delete unused proxies from the list so the app stays easy to manage.

## 📁 Suggested folder setup

For a clean setup, use one folder for the app and one for saved data:

- `C:\proxy-ipv6-generator\app`
- `C:\proxy-ipv6-generator\data`

This keeps the app files and proxy data easy to find.

## ❓ Troubleshooting

### The app does not open

- Check that Python is installed
- Make sure you downloaded the correct Windows release
- Run the app as administrator
- Reboot and try again

### The proxy does not connect

- Confirm the port is free
- Check firewall rules
- Make sure the IPv6 range is valid
- Try a fresh IP rotation

### The proxy shows dead

- Test the network interface
- Check your IPv6 source range
- Recreate the proxy list
- Run the live/dead check again

### The app cannot change IPs

- Run as administrator
- Check Windows network permissions
- Confirm the adapter name is correct
- Make sure the system supports IPv6

### Login does not work

- Check username and password
- Remove extra spaces
- Recreate the proxy config
- Test again with one proxy

## 🔧 Basic requirements for stable use

For smooth use, keep these settings in place:

- a working IPv6 connection
- a fixed network adapter
- enough free ports on your machine
- admin access on Windows
- a clean proxy list with valid entries

## 📌 Typical use cases

This app fits simple proxy work such as:

- testing apps that need IPv6
- managing many proxy entries at once
- rotating addresses for each task
- checking proxy health before use
- running local proxy tests on Windows

## 📝 File and setting tips

Keep these habits to avoid confusion:

- use one folder for the app
- save your settings before closing
- name your proxy groups in a clear way
- write down the port you use
- keep a backup of your proxy list

## 🔗 Download again

If you need the latest file, use the release page here:

[https://github.com/despiteportablecomputer411/proxy-ipv6-generator/releases](https://github.com/despiteportablecomputer411/proxy-ipv6-generator/releases)

## 🇻🇳 Hướng dẫn nhanh bằng tiếng Việt

Nếu bạn dùng tiếng Việt, quy trình cơ bản là:

1. Mở trang Releases.
2. Tải bản Windows mới nhất.
3. Giải nén file nếu cần.
4. Cài Python 3.8+ nếu máy chưa có.
5. Chạy app bằng file `.exe` hoặc file Python.
6. Chọn dải IPv6, cổng proxy, và chế độ đăng nhập.
7. Bấm tạo proxy và kiểm tra trạng thái.

## 📦 What to expect after setup

After setup, you should be able to:

- start the proxy service
- create many IPv6 proxy entries
- rotate IPs when needed
- check live status
- monitor connections
- use the app in Vietnamese or English