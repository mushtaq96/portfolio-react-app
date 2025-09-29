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
# Deployment trigger
