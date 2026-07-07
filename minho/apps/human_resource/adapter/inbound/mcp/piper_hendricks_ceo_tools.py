from mcp.server.fastmcp import FastMCP

'''
Richard Hendricks (리처드 헨드릭스)
파이드 파이퍼의 창업자 겸 CEO. 압축 알고리즘을 발명해 회사를 세웠지만 사람 다루는 일에는 늘 서툴다.
'''
mcp = FastMCP("Hendricks")

@mcp.tool(name="Hendricks")
async def introduce_myself() -> str:
    return "파이드 파이퍼 CEO 헨드릭스입니다."
