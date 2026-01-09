# Simulation Analyzer

LLM-powered deep content analysis tool for Concordia simulation logs.

## Overview

The Simulation Analyzer automatically analyzes simulation logs and generates comprehensive reports similar to manual expert analysis. It uses Large Language Models to:

- Extract structured data from HTML simulation logs
- Generate executive summaries
- Analyze team effectiveness
- Identify key insights and patterns
- Provide actionable recommendations
- Create professional markdown reports

## Installation

Install the required dependencies:

```bash
pip install beautifulsoup4 lxml
```

Or install all backend dependencies:

```bash
pip install -r backend/requirements.txt
```

## Usage

### Command Line Interface

The easiest way to use the analyzer is via the CLI script:

```bash
python backend/scripts/analyze_simulation.py <log_path> [output_path]
```

**Examples:**

```bash
# Analyze a simulation log (auto-generates output filename)
python backend/scripts/analyze_simulation.py logs/20260109_224705_simulation.html

# Specify custom output path
python backend/scripts/analyze_simulation.py logs/simulation.html reports/my_analysis.md

# Analyze the phishing simulation
python backend/scripts/analyze_simulation.py logs/20260109_224705_Sarah_Marcus_Elena_and_1_more_A_security_team_at_a_financial_services_company_ha.html
```

### Python API

You can also use the analyzer programmatically:

```python
from backend.utils.simulation_analyzer import SimulationAnalyzer
from backend.models.llm_wrappers import GLMModel

# Initialize LLM client
llm_client = GLMModel(api_key="your-api-key", model_name="glm-4.7")

# Create analyzer
analyzer = SimulationAnalyzer(llm_client)

# Run analysis
analysis = analyzer.analyze_simulation(
    log_path="logs/simulation.html",
    metadata_path="logs/simulation.metadata.json"  # Optional
)

# Save report
analyzer.save_report(analysis, "reports/analysis.md")
```

### Quick Analysis Function

For one-off analyses:

```python
from backend.utils.simulation_analyzer import analyze_simulation_from_api

analysis = analyze_simulation_from_api(
    llm_client,
    simulation_id="20260109_224705",
    log_path="logs/simulation.html"
)
```

## Report Structure

The generated report includes:

### 1. Executive Summary
- What scenario was simulated and why
- Key events and outcomes
- Team effectiveness and decision quality
- Critical insights or recommendations

### 2. Timeline of Events
- Step-by-step breakdown of the simulation
- Agent actions and decisions
- Multi-phase developments (e.g., Wave One/Wave Two attacks)

### 3. Team Effectiveness Analysis
For each agent:
- Role and primary focus
- Key contributions
- Effectiveness rating (1-5 stars) with justification
- Strengths demonstrated
- Key insights provided

### 4. Key Insights
- **Technical Analysis**: Technical findings, vulnerabilities, mechanisms
- **Human Factors**: Psychological manipulation, user behavior, culture
- **Decision Quality**: Quality of decisions, alternatives considered
- **Attack/Failure Modes**: How attacks succeeded or failures occurred
- **Learning Outcomes**: What worked well, what could be improved

### 5. Recommendations
Organized by timeframe:
- **Immediate Actions (0-30 days)**: High-priority items with expected impact
- **Medium-Term Actions (30-90 days)**: Root cause addressing
- **Long-Term Actions (90+ days)**: Strategic initiatives

## Configuration

The analyzer uses the same LLM configuration as the main Concordia application:

```bash
# .env file
LLM_PROVIDER=glm
MODEL_NAME=glm-4.7
GLM_API_KEY=your-api-key-here
```

Supported providers:
- `glm` (Zhipu AI)
- `openai` (GPT models)
- `anthropic` (Claude models)
- `gemini` (Google Gemini)

## Example Report

See [docs/phishing-simulation-analysis-report.md](../../docs/phishing-simulation-analysis-report.md) for a complete example of a manual analysis. The automated tool produces reports with similar structure and depth.

## How It Works

1. **Parse HTML Log**: Extract structured data from simulation HTML
2. **Load Metadata**: Read simulation metadata from JSON file
3. **Generate Analysis**: Use LLM to analyze each section
4. **Format Report**: Compile into professional markdown report

### Analysis Pipeline

```
HTML Log → BeautifulSoup Parser → Structured Data → LLM Analysis → Markdown Report
```

## Advanced Usage

### Custom Analysis Prompts

You can extend the `SimulationAnalyzer` class to customize analysis:

```python
class CustomAnalyzer(SimulationAnalyzer):
    def _generate_custom_insights(self, parsed_data, metadata):
        prompt = "Your custom analysis prompt here..."
        return self.llm.sample_text(prompt, max_tokens=2000)
```

### Batch Analysis

Analyze multiple simulations:

```python
import glob
from pathlib import Path

log_files = glob.glob("logs/*.html")
for log_path in log_files:
    print(f"Analyzing {log_path}...")
    analysis = analyzer.analyze_simulation(log_path)

    output_path = f"reports/{Path(log_path).stem}_analysis.md"
    analyzer.save_report(analysis, output_path)
```

### Integration with Web API

You can integrate the analyzer into the backend API:

```python
@router.post("/api/analyze-simulation")
async def analyze_simulation_endpoint(simulation_id: str):
    log_path = f"logs/{simulation_id}.html"

    analyzer = SimulationAnalyzer(get_llm_client())
    analysis = analyzer.analyze_simulation(log_path)

    return {"analysis": analysis}
```

## Limitations

- **HTML Structure**: Assumes specific HTML structure from Concordia logs
- **Token Limits**: Very long simulations may require chunking
- **LLM Quality**: Output quality depends on LLM capabilities
- **Processing Time**: Analysis may take several minutes for complex simulations

## Troubleshooting

### "HTML parsing errors"
- Ensure log file is valid HTML from Concordia
- Check that beautifulsoup4 and lxml are installed

### "LLM timeout errors"
- Increase `LLM_TIMEOUT` in `.env` (default: 250s)
- Use a faster model (e.g., `glm-4.5-flash`)

### "Empty or low-quality reports"
- Check that LLM API key is valid
- Verify LLM provider is accessible
- Try a different model or provider

## Contributing

To extend the analyzer:

1. Add new analysis methods to `SimulationAnalyzer` class
2. Update prompt templates for better results
3. Add new report sections in `_format_markdown_report()`
4. Improve HTML parsing for better data extraction

## License

Same as the main Concordia project.
