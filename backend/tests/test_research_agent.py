from backend.app.research.agent import ResearchAgent, ResearchResult

def test_research_agent_uses_injected_search():
    agent = ResearchAgent(lambda q: ResearchResult(q, "finding", ("source",)))
    result = agent.run("test query")
    assert result.findings == "finding"
    assert result.sources == ("source",)
