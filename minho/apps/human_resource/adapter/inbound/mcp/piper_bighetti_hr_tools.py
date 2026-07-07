from mcp.server.fastmcp import FastMCP

'''
Nelson 'Big Head' Bighetti (넬슨 '빅헤드' 비게티)
실력보다 운으로 늘 좋은 자리를 차지하는 인물. 이번엔 어쩌다 인사(HR) 업무를 맡았다.
'''
mcp = FastMCP("Bighetti")

@mcp.tool(name="Bighetti")
async def introduce_myself() -> str:
    return "파이드 파이퍼 인사(HR) 담당 빅헤드 비게티입니다."
