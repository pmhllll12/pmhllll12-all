from mcp.server.fastmcp import FastMCP

'''
Bertram Gilfoyle (버트럼 길포일)
파이드 파이퍼의 시스템 아키텍트. 냉소적이고 까칠하지만 서버 인프라는 누구보다 철저히 지킨다.
'''
mcp = FastMCP("Gilfoyle")

@mcp.tool(name="Gilfoyle")
async def introduce_myself() -> str:
    return "파이드 파이퍼 시스템 아키텍트 버트럼 길포일입니다."
