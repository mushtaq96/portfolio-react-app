# Personal Portfolio Website

This is a personal portfolio website built using React and Tailwind CSS. It is deployed on GitHub Pages using GitHub Actions.

## Getting Started

To get started with this project, first clone the repository and navigate to the project directory.

- `git clone` https://github.com/musthaq96/portfolio-react-app.git
- `cd portfolio-react-app`
- Next, install the dependencies by running `yarn install`.

## Available Scripts

In the project directory, you can run:

### `yarn start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `yarn build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

### Deployment to GitHub Pages

To deploy the app to GitHub Pages, run `yarn run deploy`.

## Setting up GitHub Actions for Deployment, an example

To set up GitHub Actions for deployment, follow these steps:

1. In your repository on GitHub, navigate to the "Actions" tab.
2. Click on "New workflow" and select "set up a workflow yourself".
3. Replace the content of the file with the following:

```
name: Deploy to GitHub Pages

on: push: branches: - main

jobs: build-and-deploy: runs-on: ubuntu-latest steps: - name: Checkout uses: actions/checkout@v2

- name: Set up Node.js
  uses: actions/setup-node@v2
  with:
  node-version: 16.x

- name: Install dependencies
  run: yarn install

- name: Build
  run: yarn build

- name: Deploy
  uses: peaceiris/actions-gh-pages@v3
  with:
  github_token: ${{ secrets.GITHUB_TOKEN }}
  publish_dir: ./build

```

4. Commit and push your changes.

Now, every time you push changes to the `main` branch, your app will be automatically built and deployed to GitHub Pages.



![project structure](project_structure.png)


code2prompt --exclude="node_modules/**,.venv/**,__pycache__/**,public/**,*.svg,*.ico,package-lock.json,yarn.lock,assets/" .
code2prompt backend .

Have a .env for the backend folder too.

backend % PYTHONPATH=$(pwd) pytest tests

create .documents folder to store data
.chroma_db will be the location




Browser Policy Compliance - AutoPlay Music
Automatically handles all three browser policy scenarios:
Audio is allowed (plays immediately)
User has interacted with the site (plays after interaction)
Site has been allowlisted (plays immediately)


Future To do:
1. Vite + React
Faster development experience
Better TypeScript support
More modern build tools
Easier to maintain and scale


have this in the root folder,
# Default API base URL for development
REACT_APP_API_BASE_URL=http://localhost:8000

ollama pull phi3:mini
ollama pull tinyllama (this did not work)

# Make sure your .venv is activated
source .venv/bin/activate
python document_processor.py


Usage of the AI Chat

# 🧪 **Testing Inputs for Your Portfolio Chatbot**

Here are comprehensive test inputs in both English and German to verify your value proposition enhancement works correctly:

## 🇬🇧 **English Test Inputs**

### **Basic Functionality:**
```
Hello, who is Mushtaq Bokhari?
What are your technical skills?
Tell me about your cloud experience.
```

### **Value Proposition Questions:**
```
What value do you bring to address current IT shortages?
Why should I hire you given market demands?
What's your competitive advantage in today's job market?
How do your skills address the current developer shortage?
What unique value can you offer to our company?
Why are you worth hiring in this competitive market?
How do you stand out from other candidates?
What benefits do you bring beyond technical skills?
```

### **Market-Specific Questions:**
```
How do your C# and Azure skills address market demands?
What's your availability for immediate hiring?
Can you work in both German and English teams?
How do you handle cloud migration projects?
What experience do you have with AI integration?
```

## 🇩🇪 **German Test Inputs**

### **Basic Functionality:**
```
Hallo, wer ist Mushtaq Bokhari?
Welche technischen Fähigkeiten haben Sie?
Erzählen Sie mir von Ihrer Cloud-Erfahrung.
```

### **Value Proposition Questions:**
```
Welchen Mehrwert bieten Sie bei aktuellen IT-Engpässen?
Warum sollten wir Sie bei Marktanforderungen einstellen?
Was ist Ihr Wettbewerbsvorteil auf dem heutigen Arbeitsmarkt?
Wie entsprechen Ihre Fähigkeiten dem aktuellen Entwicklermangel?
Welchen einzigartigen Wert können Sie unserem Unternehmen bieten?
Warum sind Sie eine lohnenswerte Einstellung in diesem Wettbewerbsmarkt?
Wie heben Sie sich von anderen Kandidaten ab?
Welche Vorteile bieten Sie über technische Fähigkeiten hinaus?
```

### **Market-Specific Questions:**
```
Wie entsprechen Ihre C#- und Azure-Fähigkeiten den Marktanforderungen?
Was ist Ihre Verfügbarkeit für eine sofortige Einstellung?
Können Sie in deutschen und englischen Teams arbeiten?
Wie gehen Sie mit Cloud-Migrationsprojekten um?
Welche Erfahrung haben Sie mit KI-Integration?
```
### Random notes

Cost Optimization Expert Tips 
Token Optimization Strategies: 
1. Prompt Engineering: Reduce unnecessary tokens by 30-50%
2. Caching: Cache common responses (50% cost reduction)
3. Temperature Control: Lower temperature = more predictable, shorter responses
4. Max Tokens: Set appropriate limits (500 tokens ≈ 375 words)


// German queries your chatbot should handle:
"Erzählen Sie mir von Ihren React-Erfahrungen"
"Was sind Ihre Stärken?"
"Welche Projekte haben Sie entwickelt?"
"Wie kann ich Sie kontaktieren?"

// English queries:
"Tell me about your React experience"
"What are your strengths?"
"What projects have you built?"
"How can I contact you?"


# Implement these instead of choosing cheaper model:
1. Add response caching for common queries
2. Optimize prompts to reduce token usage by 30%
3. Limit response length to essential information
4. Use prompt templates to ensure consistent, efficient queries

Agent Capabilities You DON'T Need right now : 
* Web search for current job market data
* Email integration to contact you
* Calendar scheduling for interviews
* File analysis beyond your pre-loaded docs
* Real-time data fetching

	Creating a separate Embedding API is the most optimal solution right now because it moves the memory-heavy task of loading the AI model away from your main website's backend, ensuring your website stays fast and doesn't crash, especially when you deploy it for free online where computer power is limited.
*  

The external Embedding API acts as a robust fallback plan, ensuring the chat works smoothly for the recruiter regardless of the specific memory behavior of ChromaDB's persistence on Render. It demonstrates good engineering practices (separation of concerns, planning for scalability/performance) which are positive signals in a portfolio project.
y pointing directly to the snapshot directory, we are telling sentence-transformers exactly where the config.json, model.safetensors, and other necessary files are located, bypassing potential issues with the higher-level repository structure that might be confusing it.

To simplify deployment and ensure consistency, the featureAI branch (containing the embedding_api code and large LFS-tracked model files) was merged into main. This allows both the portfolio-backend (which needs the .chroma_db index) and the mushtaq-embedding-api services to be deployed from the same, stable main branch on Render. This avoids managing deployments from multiple branches and keeps all necessary runtime assets together, despite the increased repository size due to LFS files. 
 

Based on Your Previous Findings: 
* You already know that paraphrase-multilingual-MiniLM-L12-v2 () works for your needs (English + German) but is large (915MB).
You found paraphrase-MiniLM-L6-v2 (), which is small and good for English, but not explicitly trained for German (though it might still produce usable embeddings).

https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

Before I had used this 
https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2


When to run? ‘git lfs status  ‘
