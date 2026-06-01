#!/bin/bash
# NeuroTutor AI — Setup Script (Google Gemini Edition)

BOLD="\033[1m"; GREEN="\033[0;32m"; CYAN="\033[0;36m"; YELLOW="\033[0;33m"; RED="\033[0;31m"; RESET="\033[0m"

echo -e "\n${CYAN}${BOLD}"
echo "  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗ "
echo "  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗"
echo "  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║"
echo "  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║"
echo "  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝"
echo -e "${RESET}${BOLD}   NeuroTutor AI — Google Gemini Edition${RESET}\n"

echo -e "${CYAN}[1/5]${RESET} Checking Python 3..."
python3 --version || { echo -e "${RED}❌ Python 3 required — install from python.org${RESET}"; exit 1; }

echo -e "${CYAN}[2/5]${RESET} Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo -e "    ${GREEN}✅ venv ready${RESET}"

echo -e "${CYAN}[3/5]${RESET} Installing packages (may take 2-4 minutes)..."
pip install --upgrade pip -q
pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-socketio flask-cors flask-jwt-extended -q
pip install google-generativeai langchain langchain-google-genai langchain-community langchain-core langgraph -q
pip install python-dotenv pydantic python-jose passlib eventlet plotly -q
echo -e "    ${GREEN}✅ Packages installed${RESET}"

echo -e "${CYAN}[4/5]${RESET} Setting up environment..."
[ ! -f ".env" ] && cp .env.example .env && echo -e "    ${YELLOW}⚠️  Created .env — add your GEMINI_API_KEY${RESET}" || echo -e "    ${GREEN}✅ .env exists${RESET}"
mkdir -p data/chroma_db

echo -e "${CYAN}[5/5]${RESET} Checking API key..."
if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
  echo ""
  echo -e "${YELLOW}╔════════════════════════════════════════════╗${RESET}"
  echo -e "${YELLOW}║  ⚠️  ADD YOUR FREE GEMINI API KEY          ║${RESET}"
  echo -e "${YELLOW}╠════════════════════════════════════════════╣${RESET}"
  echo -e "${YELLOW}║  1. Go to: aistudio.google.com/app/apikey  ║${RESET}"
  echo -e "${YELLOW}║  2. Sign in with Google (FREE)              ║${RESET}"
  echo -e "${YELLOW}║  3. Click 'Create API Key'                  ║${RESET}"
  echo -e "${YELLOW}║  4. Open .env and paste your key:           ║${RESET}"
  echo -e "${YELLOW}║     GEMINI_API_KEY=AIza...your_key          ║${RESET}"
  echo -e "${YELLOW}╚════════════════════════════════════════════╝${RESET}"
else
  echo -e "    ${GREEN}✅ Gemini API key configured${RESET}"
fi

echo ""
echo -e "${GREEN}${BOLD}╔════════════════════════════════════╗${RESET}"
echo -e "${GREEN}${BOLD}║  ✅ Setup complete!                 ║${RESET}"
echo -e "${GREEN}${BOLD}╚════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}Start the server:${RESET}"
echo -e "  ${CYAN}  source venv/bin/activate${RESET}"
echo -e "  ${CYAN}  python app.py${RESET}"
echo ""
echo -e "  ${BOLD}Open in browser:${RESET}"
echo -e "  ${CYAN}  http://localhost:5000${RESET}"
echo ""
