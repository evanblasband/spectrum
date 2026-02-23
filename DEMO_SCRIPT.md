# Spectrum Demo Video Script

**Total Runtime: ~2 minutes**

---

## INTRO (10 seconds)

> "This is Spectrum - a political bias analyzer for news articles. Paste any news URL, and it shows you where the article falls on the political spectrum, finds related coverage from other sources, and lets you compare how different outlets frame the same story."

---

## DEMO: ANALYZE AN ARTICLE (30 seconds)

*[Paste a URL from a supported source like NPR, Fox News, or BBC]*

> "Let's analyze this article. I'll paste the URL and hit analyze."

*[Wait for results]*

> "The app extracts the article content, sends it to an AI model, and returns a political leaning score from negative one - far left - to positive one - far right. You also get a confidence score, the AI's reasoning, and key topics and points extracted from the article."

---

## DEMO: RELATED ARTICLES (15 seconds)

*[Scroll to related articles section]*

> "Below the analysis, Spectrum automatically finds related articles covering the same story from different sources. I can analyze any of these with one click to see how other outlets are framing this topic."

---

## DEMO: COMPARISON (20 seconds)

*[Add articles to comparison tray and compare]*

> "The real power is in comparison. I'll add a couple articles to the comparison tray and hit compare. Now I can see both articles on the same spectrum, their shared topics, and where they agree or disagree."

---

## UNDER THE HOOD (20 seconds)

> "Under the hood, Spectrum uses FastAPI on the backend with a clean architecture pattern. Article content is scraped and sent to Groq's Llama 3.3 model for analysis. NewsAPI powers the related article discovery. The frontend is React with TypeScript, and everything is rate-limited and cached to keep API costs down."

---

## FUTURE IMPROVEMENTS (15 seconds)

> "Future plans include a browser extension - which would solve scraping limitations and work with paywalled sites you subscribe to - improved same-story detection using AI to match articles about the same event, and user accounts to save your analysis history."

---

## OUTRO (10 seconds)

> "Spectrum is open source - check out the GitHub link for the full documentation, architecture diagrams, and tech decisions. Thanks for watching!"

---

## Suggested Test URLs

Use these for the demo (fully supported sources):

- **NPR**: https://www.npr.org (center-left)
- **BBC**: https://www.bbc.com/news (center)
- **Fox News**: https://www.foxnews.com (right)
- **The Guardian**: https://www.theguardian.com (left)
- **Breitbart**: https://www.breitbart.com (far-right)

Pick articles on the same topic for the comparison demo.
