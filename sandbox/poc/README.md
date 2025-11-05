# AI Pilot Assessment Engine - POC

Minimal proof-of-concept implementing Steps 1-8 of the output-centric assessment flow.

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your GCP project details
```

### 2. Run Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_taxonomy_loader.py

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### 3. Run Application

```bash
streamlit run app.py
```

## Project Structure

```
poc/
├── app.py                      # Streamlit main app
├── requirements.txt            # Dependencies
├── pytest.ini                  # Test configuration
├── .env.template               # Environment template
├── .gitignore                  # Git ignore
│
├── config/
│   └── settings.py            # Configuration management
│
├── core/
│   ├── taxonomy_loader.py     # Load JSON taxonomies
│   ├── session_manager.py     # Session state management
│   └── gemini_client.py       # Vertex AI / Gemini integration
│
├── engines/
│   ├── discovery.py           # Output discovery engine
│   ├── assessment.py          # Component assessment engine
│   └── recommender.py         # Pilot recommendation engine
│
├── models/
│   └── data_models.py         # Pydantic data models
│
├── utils/
│   └── helpers.py             # Utility functions
│
└── tests/
    ├── unit/                  # Unit tests
    ├── integration/           # Integration tests
    └── fixtures/              # Test fixtures
```

## Testing

### Requirements
- **Unit tests** for all functions/methods
- **Integration tests** for end-to-end flows
- **Minimum 80% code coverage**
- **CI/CD ready** - tests run on every deployment

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov

# Specific test
pytest tests/unit/test_taxonomy_loader.py::test_load_function_templates
```

### Test Structure

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test complete flows (discovery → assessment → recommendation)
- **Fixtures**: Reusable test data and mocks

## Development

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy core/ engines/ models/
```

### Adding New Features

1. Write tests first (TDD)
2. Implement feature
3. Run tests: `pytest`
4. Check coverage: `pytest --cov`
5. Format code: `black .`

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Cloud Run (Production)
```bash
# Build Docker image
docker build -t gcr.io/${GCP_PROJECT_ID}/assessment-poc .

# Push to GCR
docker push gcr.io/${GCP_PROJECT_ID}/assessment-poc

# Deploy to Cloud Run
gcloud run deploy assessment-poc \
  --image gcr.io/${GCP_PROJECT_ID}/assessment-poc \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Architecture

This POC implements the **output-centric assessment model** from `docs/1_functional_spec/domain_model.md`:

1. **Output Discovery** - Identify output from user description
2. **Context Inference** - Infer Team, Process, System
3. **Confirmation** - User validates context
4. **Component Assessment** - Rate 4 components (⭐ 1-5)
5. **MIN Calculation** - Calculate actual quality
6. **Required Quality** - User provides target
7. **Gap Analysis** - Identify bottleneck
8. **Pilot Recommendation** - Suggest 2-3 pilots

## Documentation

- **Technical Spec**: `../docs/2_technical_spec/POC_TECHNICAL_SPEC.md`
- **Implementation Tasks**: `../POC_IMPLEMENTATION_TASKS.md`
- **Domain Model**: `../docs/1_functional_spec/domain_model.md`
- **Data Taxonomies**: `../src/data/README.md`

## License

Internal use only.
