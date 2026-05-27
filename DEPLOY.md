# Deploy Comp-XM Simulator

## Option 1: Streamlit Community Cloud (Recommended — FREE)

### Prerequisites
- GitHub account (free at github.com)
- Streamlit Cloud account (free at share.streamlit.io)

### Steps

1. **Create GitHub repo**
   ```powershell
   cd "F:\Claude CODE\CAPSIM"
   git init
   git add sim/ requirements.txt .streamlit/ .gitignore DEPLOY.md
   git commit -m "Initial commit: Comp-XM 2026 simulator"
   ```

2. **Create repo on GitHub** (web):
   - Go to https://github.com/new
   - Name: `compxm-sim` (or whatever)
   - Public or Private (both work)
   - Don't initialize with README

3. **Push to GitHub**
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/compxm-sim.git
   git branch -M main
   git push -u origin main
   ```

4. **Deploy on Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Repository: `YOUR_USERNAME/compxm-sim`
   - Branch: `main`
   - Main file path: `sim/app.py`
   - App URL (custom subdomain): `compxm-andrews` (or whatever)
   - Click **Deploy**

5. **Wait ~3 minutes** while Streamlit installs deps and starts the app.

6. **Done!** Your URL will be `https://compxm-andrews.streamlit.app`
   - Share with anyone — they just open the URL
   - Auto-redeploys when you `git push` updates

---

## Option 2: ngrok (Quick share, your PC stays on)

If you don't want to deploy to cloud and just want to share temporarily:

1. **Download ngrok**: https://ngrok.com/download
2. **Sign up** (free) and get authtoken
3. **Setup**:
   ```powershell
   ngrok config add-authtoken YOUR_TOKEN
   ```
4. **Run your Streamlit locally** (port 8501)
5. **Expose**:
   ```powershell
   ngrok http 8501
   ```
6. Share the `https://xxxxx.ngrok.io` URL — anyone can use it

**Pros**: Fast (no GitHub needed), no upload
**Cons**: Your PC must be ON; URL changes each session (paid plan = fixed URL)

---

## Option 3: Hugging Face Spaces (FREE alternative)

1. Sign up at https://huggingface.co
2. Create new Space → Streamlit template
3. Upload your files via web or git
4. Auto-deploys, get URL like `https://yourname-compxm.hf.space`

Free, no sleep, but slightly more setup than Streamlit Cloud.

---

## Option 4: Docker (advanced — for company servers)

Build a Docker image:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "sim/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Run anywhere with Docker installed:
```bash
docker build -t compxm-sim .
docker run -p 8501:8501 compxm-sim
```

---

## Comparison

| Option | "No install for user?" | Setup time | Cost | URL stays? |
|---|---|---|---|---|
| **Streamlit Cloud** | ✅ YES | 10 min | Free | ✅ Permanent |
| **ngrok** | ✅ YES | 5 min | Free (URL changes) | ❌ Temp |
| **Hugging Face** | ✅ YES | 15 min | Free | ✅ Permanent |
| **Docker** | ❌ Need Docker | 20 min | Varies | Depends |

**Recommendation**: Streamlit Cloud for permanent sharing, ngrok for one-off demos.
