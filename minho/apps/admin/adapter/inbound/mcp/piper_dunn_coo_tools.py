from mcp.server.fastmcp import FastMCP

'''
Jared Dunn (자레드 던)
파이드 파이퍼의 COO. 헌신적이고 충성스러운 운영 책임자로 회사를 위해 무엇이든 내어준다.
'''
mcp = FastMCP("Dunn")

@mcp.tool(name="Dunn")
async def introduce_myself() -> str:
    return "파이드 파이퍼 COO 자레드 던입니다."
