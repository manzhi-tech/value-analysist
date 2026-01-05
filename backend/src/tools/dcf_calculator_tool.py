from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DCFCalculatorInput(BaseModel):
    net_income: float = Field(..., description="基准年的净利润 (Net Income)。")
    depreciation_amortization: float = Field(..., description="基准年的折旧与摊销 (D&A)。")
    capex: float = Field(..., description="基准年的资本支出 (Capex) (应为正数，表示流出)。")
    growth_rate: float = Field(..., description="前 10 年所有者收益的预期年增长率 (例如 0.05 代表 5%)。")
    terminal_growth_rate: float = Field(0.02, description="10 年后的永续增长率 (Terminal Value)，通常为 2%-3%。")
    discount_rate: float = Field(..., description="折现率 (必要回报率)，例如 0.10 代表 10%。")
    years: int = Field(10, description="预测期年数。")

class DCFCalculatorTool(BaseTool):
    name: str = "Buffett Owner Earnings DCF Calculator"
    description: str = (
        "Calculates the Intrinsic Value of a business using the Warren Buffett Shareholder Earnings Discounted Cash Flow model. "
        "Owner Earnings = Net Income + Depreciation - Capex."
    )
    args_schema: Type[BaseModel] = DCFCalculatorInput

    def _run(self, net_income: float, depreciation_amortization: float, capex: float, 
             growth_rate: float, terminal_growth_rate: float, discount_rate: float, years: int) -> str:
        
        # 1. Calculate Base Owner Earnings
        # Capex is usually negative in specific cash flows, but here we treat it as an outlay to subtract.
        # If input capex is 150000, we subtract 150000.
        owner_earnings = net_income + depreciation_amortization - abs(capex)
        
        projected_cash_flows = []
        cumulative_discounted_cash_flow = 0.0
        
        current_cf = owner_earnings
        
        explanation = f"基准所有者收益 (Owner Earnings): {owner_earnings:,.2f} (净利润: {net_income} + D&A: {depreciation_amortization} - Capex: {capex})\n"
        explanation += f"假设: 增长率: {growth_rate:.1%}, 折现率: {discount_rate:.1%}, 永续增长率: {terminal_growth_rate:.1%}\n\n"
        explanation += "| 年份 | 预测所有者收益 | 折现因子 | 现值 |\n"
        explanation += "|---|---|---|---|\n"

        # 2. Projection Phase
        for i in range(1, years + 1):
            current_cf = current_cf * (1 + growth_rate)
            discount_factor = 1 / ((1 + discount_rate) ** i)
            present_value = current_cf * discount_factor
            
            cumulative_discounted_cash_flow += present_value
            projected_cash_flows.append(present_value)
            
            explanation += f"| {i} | {current_cf:,.0f} | {discount_factor:.4f} | {present_value:,.0f} |\n"

        # 3. Terminal Value
        # TV = (Final Year CF * (1 + Terminal Growth)) / (Discount Rate - Terminal Growth)
        final_year_cf = current_cf
        terminal_value = (final_year_cf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        present_terminal_value = terminal_value / ((1 + discount_rate) ** years)
        
        explanation += f"\n终值 (第 {years} 年后): {terminal_value:,.0f}\n"
        explanation += f"终值的现值: {present_terminal_value:,.0f}\n"
        
        # 4. Total Value
        intrinsic_value = cumulative_discounted_cash_flow + present_terminal_value
        explanation += f"\n**企业内在总价值**: {intrinsic_value:,.2f}"
        
        return explanation
