# How to Add Screenshots

Save your screenshots here with these **exact filenames**:

| Filename | What to Capture |
|---|---|
| `landing.png` | The public home page at `http://localhost:5000` |
| `dashboard.png` | The student dashboard showing XP, streak, recent sessions |
| `tutor_chat.png` | The AI Tutor chat — show the Agent Pipeline sidebar open |
| `quiz.png` | A quiz in progress — show the MCQ options and score panel |
| `pdf_chat.png` | PDF Chat — show uploaded doc on left, AI answer on right |
| `predictor.png` | Performance Predictor — show predicted scores + mastery levels |
| `analytics.png` | Analytics — show the score trend chart and subject bar chart |
| `study_plans.png` | A generated 4-week study plan |
| `leaderboard.png` | The leaderboard with XP rankings |
| `register.png` | The 3-step registration wizard |

## Tips for good screenshots

- Use a **1280 × 800** or wider browser window
- The dark theme looks best — make sure dark mode is ON
- For the tutor chat, click a few messages first so the conversation is visible
- For the predictor, take at least 3 quizzes first so the RF model has data

## After saving screenshots

```bash
git add screenshots/
git commit -m "Add project screenshots"
git push
```

The images will appear in the README automatically on GitHub.
