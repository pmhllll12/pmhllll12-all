from mcp.server.fastmcp import FastMCP

'''
Dinesh Chugtai (디네시 추그타이)
파이드 파이퍼의 엔지니어. 길포일과 늘 자존심 대결을 벌이는 코더.
'''
mcp = FastMCP("Dinesh")

@mcp.tool(name="Dinesh")
async def introduce_myself() -> str:
    return "파이드 파이퍼 엔지니어 디네시 추그타이입니다."
