#!/bin/bash

echo "🚀 Creating JD-Vector project structure..."

# Root directories
mkdir -p apps/web apps/server packages/shared-types packages/config data-lab/notebooks data-lab/datasets data-lab/scripts docs/api .github/workflows

# Frontend structure (apps/web)
echo "📦 Creating Frontend structure..."
mkdir -p apps/web/src/{app,components/{ui,layout,upload,analysis,roadmap,common},pages,hooks,services,store,types,utils,styles}
mkdir -p apps/web/public/assets
mkdir -p apps/web/tests/{components,hooks,utils}

# Backend structure (apps/server)
echo "🐍 Creating Backend structure..."
mkdir -p apps/server/app/{api/v1/endpoints,core/{rag,llm,analysis},models,services,db/migrations,utils}
mkdir -p apps/server/tests/{api,core,services}
mkdir -p apps/server/scripts

# Create essential Frontend files
echo "📝 Creating Frontend files..."
touch apps/web/src/app/{App.tsx,App.css,main.tsx}
touch apps/web/src/pages/{HomePage,UploadPage,AnalysisPage,ResultPage,RoadmapPage,NotFoundPage}.tsx
touch apps/web/src/components/ui/{Button,Card,Input,Modal,Progress,Toast}.tsx
touch apps/web/src/components/layout/{Header,Sidebar,Footer,DashboardLayout}.tsx
touch apps/web/src/components/upload/{FileUpload,PDFViewer,TextInput,UploadProgress}.tsx
touch apps/web/src/components/analysis/{RadarChart,MatchScore,SkillGapList,ComparisonTable}.tsx
touch apps/web/src/components/roadmap/{RoadmapTimeline,TodoChecklist,ResourceCard,ProgressTracker}.tsx
touch apps/web/src/components/common/{Loading,ErrorBoundary,ThemeToggle}.tsx
touch apps/web/src/hooks/{useFileUpload,useAnalysis,useSupabase,useTheme,useLocalStorage}.ts
touch apps/web/src/services/{api,uploadService,analysisService,roadmapService,supabaseClient}.ts
touch apps/web/src/store/{useAppStore,useUploadStore,useAnalysisStore,useUserStore}.ts
touch apps/web/src/types/{api.types,analysis.types,upload.types,roadmap.types}.ts
touch apps/web/src/utils/{format,validation,chartHelpers,constants}.ts
touch apps/web/src/styles/index.css
touch apps/web/index.html
touch apps/web/{vite.config.ts,tsconfig.json,tsconfig.node.json,tailwind.config.ts,postcss.config.js}
touch apps/web/{.eslintrc.json,.prettierrc,.env.example,vercel.json}
touch apps/web/README.md

# Create essential Backend files
echo "🔧 Creating Backend files..."
touch apps/server/app/api/v1/endpoints/{__init__,upload,analysis,roadmap,health}.py
touch apps/server/app/api/v1/{__init__,router}.py
touch apps/server/app/api/{__init__,deps}.py
touch apps/server/app/core/{__init__,config,security,logging}.py
touch apps/server/app/core/rag/{__init__,document_loader,text_splitter,embeddings,vector_store,retriever}.py
touch apps/server/app/core/llm/{__init__,client,prompts,chains,agents}.py
touch apps/server/app/core/analysis/{__init__,similarity,skill_extractor,gap_analyzer,score_calculator}.py
touch apps/server/app/models/{__init__,schemas,database,enums}.py
touch apps/server/app/services/{__init__,upload_service,analysis_service,roadmap_service,storage_service}.py
touch apps/server/app/db/{__init__,session,base}.py
touch apps/server/app/utils/{__init__,pdf_parser,text_processor,validators}.py
touch apps/server/app/__init__.py
touch apps/server/main.py
touch apps/server/tests/conftest.py
touch apps/server/{pyproject.toml,poetry.lock,alembic.ini,.env.example,.flake8,.python-version,fly.toml}
touch apps/server/README.md

# Shared packages
echo "📦 Creating shared packages..."
mkdir -p packages/shared-types/src
mkdir -p packages/config/eslint-config
mkdir -p packages/config/tsconfig
touch packages/shared-types/src/{index,api,models}.ts
touch packages/shared-types/{package.json,tsconfig.json,README.md}
touch packages/config/eslint-config/{index.js,package.json}
touch packages/config/tsconfig/{base.json,react.json,package.json}

# Data lab
echo "🔬 Creating data lab..."
touch data-lab/notebooks/{01_similarity_analysis,02_embedding_experiments,03_score_calibration}.ipynb
touch data-lab/datasets/README.md
touch data-lab/scripts/{prepare_data,evaluate_model}.py
touch data-lab/{requirements.txt,README.md}

# Docs
echo "📚 Creating documentation..."
touch docs/{architecture,deployment,development}.md
touch docs/api/openapi.yaml

# GitHub workflows
echo "⚙️ Creating GitHub workflows..."
touch .github/workflows/{ci-frontend,ci-backend,lint}.yml

echo "✅ Project structure created successfully!"
echo ""
echo "📁 Directory tree:"
echo "jd-vector/"
echo "├── apps/"
echo "│   ├── web/          # Frontend (React + Vite + TypeScript)"
echo "│   └── server/       # Backend (FastAPI + LangChain)"
echo "├── packages/"
echo "│   ├── shared-types/ # 공통 TypeScript 타입"
echo "│   └── config/       # 공통 설정"
echo "├── data-lab/         # 데이터 분석 실험"
echo "├── docs/             # 문서"
echo "└── scripts/          # 유틸리티 스크립트"
echo ""
echo "🎯 Next steps:"
echo "1. Create root config files: package.json, pnpm-workspace.yaml, .gitignore, .nvmrc"
echo "2. Set up Frontend: cd apps/web && pnpm install"
echo "3. Set up Backend: cd apps/server && poetry install"
echo "4. Configure environment variables (.env files)"
echo "5. Start development: pnpm dev (Frontend) && pnpm dev:server (Backend)"
