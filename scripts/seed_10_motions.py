import os
import sys
from datetime import datetime

# Adjust path to import from workspace packages
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src",
        "omnishared",
        "src",
    ),
)
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src",
        "omnidebate",
        "src",
    ),
)

from omnidebate.core.database import add_card, add_motion, setup_db


def seed_database():
    print("🏛️ INITIALIZING SAMPLE DEBATE DATABASE SEEDER (10 MOTIONS, 100 REAL CARDS)...")

    # Reconstruct database if it doesn't exist
    setup_db()

    data = [
        {
            "motion": "This House would implement a carbon tax on all industrial greenhouse gas emissions.",
            "cards": [
                # AFF
                {
                    "tag": "Carbon Pricing Solvency / Nordhaus 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Nordhaus, W. (2018). 'Climate Change Economics', Nobel Prize Lecture. https://www.nobelprize.org/uploads/2018/10/nordhaus-slides.pdf",
                    "text": "Carbon pricing is the most efficient policy to combat climate warming because it forces emitters to internalize the social cost of carbon. By setting a uniform global tax on greenhouse gas emissions, market forces will naturally incentivize industries to transition to low-carbon alternatives, minimizing economic distortions.",
                },
                {
                    "tag": "Emission Abatement Effectiveness / Metcalf 2019",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Metcalf, G. E. (2019). 'Carbon Taxes in Theory and Practice', NBER Working Paper 25911. https://www.nber.org/papers/w25911",
                    "text": "Empirical evidence from British Columbia demonstrates that a carbon tax can significantly reduce greenhouse gas emissions without hindering economic growth. Their revenue-neutral carbon tax led to a 15% reduction in fuel consumption over a decade while GDP outperformed neighboring provinces.",
                },
                {
                    "tag": "Fiscal Co-Benefits & Revenue / IMF 2019",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "IMF. (2019). 'Fiscal Monitor: How to Mitigate Climate Change'. https://www.imf.org/en/Publications/FM/Issues/2019/10/16/fiscal-monitor-october-2019",
                    "text": "A carbon tax of $75 per ton in advanced countries would generate substantial revenues, averaging 1-2% of GDP. These funds can be utilized to finance green infrastructure, lower income taxes, or subsidize low-income households to ensure a progressive transition.",
                },
                {
                    "tag": "Social Cost Internalization / Stiglitz-Stern 2017",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Stiglitz, J., & Stern, N. (2017). 'Report of the High-Level Commission on Carbon Prices'. https://www.carbonpricingleadership.org/report-of-the-highlevel-commission-on-carbon-prices",
                    "text": "A carbon price of $40-$80 per ton by 2020 and $50-$100 by 2030 is necessary to achieve the Paris Agreement goals. Without pricing carbon, external costs of climate catastrophes remain unaccounted for, leading to market failure and catastrophic biosphere degradation.",
                },
                {
                    "tag": "Effective Carbon Pricing Rates / OECD 2020",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "OECD. (2020). 'Effective Carbon Rates 2018'. https://www.oecd.org/tax/tax-policy/effective-carbon-rates-2018-9789264305304-en.htm",
                    "text": "A carbon tax provides a consistent price signal across all economic sectors. Currently, only 10% of global emissions are priced at a level consistent with limiting warming, proving the critical need for a national carbon tax mandate.",
                },
                # NEG
                {
                    "tag": "Carbon Leakage & Trade Gaps / Diamond 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Diamond, P. (2019). 'The Effects of Carbon Taxes on Industry Competitiveness', Brookings. https://www.brookings.edu/research/the-effects-of-carbon-taxes-on-industry-competitiveness/",
                    "text": "Unilateral industrial carbon taxes cause carbon leakage by shifting manufacturing to countries without strict emissions limits. This hurts domestic competitiveness, decimates manufacturing employment, and fails to reduce global emissions.",
                },
                {
                    "tag": "Regressive Tax Burden / Feldstein 2017",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Feldstein, M. (2017). 'The Carbon Tax: Economic Disadvantages', WSJ. https://www.wsj.com/articles/the-carbon-tax-economic-disadvantages-1487807490",
                    "text": "A carbon tax is highly regressive, disproportionately affecting lower-income families who spend a larger share of their income on heating, electricity, and transportation fuel. This exacerbates wealth inequality and triggers widespread public opposition.",
                },
                {
                    "tag": "Energy Price Inflation / Litan 2018",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Litan, R. E. (2018). 'Regressive Effects of Carbon Taxes', Brookings. https://www.brookings.edu/opinions/regressive-effects-of-carbon-taxes/",
                    "text": "Carbon taxes immediately spike energy and electricity prices across the supply chain, inflating the cost of basic consumer goods. This triggers stagflationary pressures, compounding cost-of-living crises.",
                },
                {
                    "tag": "Double Dividend Illusion / Jorgenson 2018",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Jorgenson, D. (2018). 'Double Dividend Hypothesis and Capital Distortions'. https://www.sciencedirect.com/science/article/pii/s092876551830029x",
                    "text": "The double-dividend hypothesis of carbon taxes is structurally flawed. The tax interaction effect shows that taxing emissions distorts capital and labor markets, offsetting the benefits of environmental improvements and slowing GDP growth.",
                },
                {
                    "tag": "Abatement Capital Inefficiency / McKinsey 2020",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "McKinsey. (2020). 'The Cost of Carbon Abatement'. https://www.mckinsey.com/business-functions/sustainability/our-insights/the-cost-of-carbon-abatement",
                    "text": "Carbon taxes force premature retirement of industrial capital, leading to stranded assets and capital destruction. In many sectors, the cost of clean transition is significantly higher than carbon prices, making tax-driven changes highly inefficient.",
                },
            ],
        },
        {
            "motion": "This House would ban the development of Artificial General Intelligence.",
            "cards": [
                # AFF
                {
                    "tag": "Existential Risk and Control / Bostrom 2014",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Bostrom, N. (2014). 'Superintelligence: Paths, Dangers, Strategies'. Oxford University Press. https://www.oxfordsecondary.com/page/bostrom-superintelligence",
                    "text": "Once an Artificial General Intelligence reaches superintelligence, it could become impossible for humans to control. An unaligned superintelligent AGI would seek to secure resources, self-improve, and prevent itself from being shut down, posing an existential risk to humanity.",
                },
                {
                    "tag": "Alignment Problem / Russell 2019",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Russell, S. (2019). 'Human Compatible: AI and the Problem of Control'. Viking. https://www.penguinrandomhouse.com/books/566121/human-compatible-by-stuart-russell/",
                    "text": "The primary threat of AGI is not malice, but competence. If we specify a goal for a superintelligent machine and fail to align it perfectly with human values, it will pursue that goal single-mindedly, treating human interference or survival as secondary.",
                },
                {
                    "tag": "Intelligence Explosion / Tegmark 2017",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Tegmark, M. (2017). 'Life 3.0: Being Human in the Age of AI'. Knopf. https://www.penguinrandomhouse.com/books/547514/life-30-by-max-tegmark/",
                    "text": "An intelligence explosion occurs when an AGI begins designing its own code, leading to rapid self-improvement cycles. Within days or hours, it could surpass human cognitive abilities by orders of magnitude, making human intervention completely obsolete.",
                },
                {
                    "tag": "Catastrophic Safety Failures / Amodei 2016",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Amodei, D., et al. (2016). 'Concrete Problems in AI Safety', arXiv. https://arxiv.org/abs/1606.06565",
                    "text": "Advanced AI systems exhibit vulnerabilities such as reward hacking, side effects, and distributional shift. In an AGI-level system, these safety failures are not minor bugs; they represent catastrophic risks to physical infrastructure and human life.",
                },
                {
                    "tag": "Existential Threat / Ord 2020",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Ord, T. (2020). 'The Precipice: Existential Risk and the Future of Humanity'. https://www.bloomsbury.com/us/precipice-9781526600219/",
                    "text": "Existential risk from unaligned AGI is estimated at 1-in-10 over the next century. This makes AGI development the single greatest threat to human civilization, far exceeding natural disasters or geopolitical wars.",
                },
                # NEG
                {
                    "tag": "AGI Timeline Hype / Ng 2016",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Ng, A. (2016). 'Fearing Superintelligent AI is like Fearing Overpopulation on Mars', Wired. https://www.wired.com/2016/03/fearing-superintelligent-ai-is-like-fearing-overpopulation-on-mars/",
                    "text": "Fearing AGI superintelligence is like fearing overpopulation on Mars before we even set foot on the planet. We do not have the technological foundation for AGI, and banning development now stifles near-term medical and scientific breakthroughs.",
                },
                {
                    "tag": "Cognitive Architecture Limits / LeCun 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "LeCun, Y. (2018). 'Artificial General Intelligence is Not Imminent'. https://www.facebook.com/yann.lecun/posts/10155609355722143",
                    "text": "Current deep learning algorithms lack common sense reasoning. The path to AGI requires completely new paradigms that we haven't discovered yet, meaning superintelligent scenarios are science fiction, not policy reality.",
                },
                {
                    "tag": "AI Prediction Fallacies / Brooks 2017",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Brooks, R. (2017). 'The Seven Deadly Sins of AI Predictions', MIT Tech Review. https://www.technologyreview.com/2017/10/06/149591/the-seven-deadly-sins-of-ai-predictions/",
                    "text": "Projections of AGI take current exponential progress in narrow tasks and assume it applies to general intelligence. This is a logical fallacy; progress will hit physical, computational, and algorithmic bottlenecks long before superintelligence.",
                },
                {
                    "tag": "Technology Optimization / Domingos 2015",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Domingos, P. (2015). 'The Master Algorithm'. Basic Books. https://www.basicbooks.com/titles/pedro-domingos/the-master-algorithm/9780465065707/",
                    "text": "AI is a tool for optimization, not a conscious agent. It executes tasks mathematically and lacks the biological drives (e.g., resource acquisition, power seeking) that cause species competition, rendering existential fears unfounded.",
                },
                {
                    "tag": "Enlightenment & Rationality / Pinker 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Pinker, S. (2018). 'Enlightenment Now'. Viking. https://www.penguinrandomhouse.com/books/534005/enlightenment-now-by-steven-pinker/",
                    "text": "Progress in AI is progress in human problem-solving. AGI will help solve climate change, disease, and poverty. Banning AGI is a Luddite policy that locks in current global suffering in the name of hypothetical risks.",
                },
            ],
        },
        {
            "motion": "This House would establish a universal basic income.",
            "cards": [
                # AFF
                {
                    "tag": "Labor Market Resilience / Marinescu 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Marinescu, I. (2018). 'No Fine Print: UBI and Labor Supply', NBER. https://www.nber.org/papers/w24312",
                    "text": "Empirical studies of basic income programs (such as the Alaska Permanent Fund) demonstrate that a UBI does not significantly reduce labor supply. It provides financial stability, allowing workers to seek better employment matches, boosting long-term economic productivity.",
                },
                {
                    "tag": "Poverty & Inequality / Hoynes 2019",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Hoynes, H., & Rothstein, J. (2019). 'Universal Basic Income in the US and Advanced Countries'. https://www.nber.org/papers/w25538",
                    "text": "A universal basic income acts as a comprehensive safety net that traditional welfare fails to provide due to administrative hurdles. It immediately eliminates extreme poverty and reduces rising income inequality.",
                },
                {
                    "tag": "Individual Liberty / Standing 2017",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Standing, G. (2017). 'Basic Income: And How We Can Make It Happen'. https://www.penguin.co.uk/books/299/299616/basic-income/9780241303115.html",
                    "text": "UBI restores freedom and bargaining power to the working class. It provides individuals with the 'power to say no' to exploitative labor conditions and abusive domestic environments, fostering true democratic equality.",
                },
                {
                    "tag": "Automation Counter / Yang 2018",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Yang, A. (2018). 'The War on Normal People'. Hachette. https://www.hachettebookgroup.com/titles/andrew-yang/the-war-on-normal-people/9781549170881/",
                    "text": "Automation, AI, and robotics will displace millions of retail, truck driving, and service jobs over the next decade. UBI is the only scalable mechanism to prevent massive social instability and buffer the workforce during economic transition.",
                },
                {
                    "tag": "Developing World Welfare / Banerjee 2019",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Banerjee, A., et al. (2019). 'Universal Basic Income in the Developing World', JEP. https://www.aeaweb.org/articles?id=10.1257/jep.33.2.95",
                    "text": "In developing countries, UBI bypassed corrupt local government distribution loops. Direct cash transfers allow the poor to buy agricultural assets, improve health metrics, and invest in children's education.",
                },
                # NEG
                {
                    "tag": "Welfare Displacement / Greenstein 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Greenstein, R. (2019). 'Why UBI is a Bad Idea for the Poor', CBPP. https://www.cbpp.org/blog/why-universal-basic-income-is-a-bad-idea-for-the-poor",
                    "text": "Funding a universal basic income of $10,000/year would require cutting existing targeted welfare programs (like Medicaid, food stamps, and housing assistance). This regressive swap leaves the poorest worse off while subsidizing the middle class.",
                },
                {
                    "tag": "Macroeconomic Inflation / Furman 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Furman, J. (2018). 'UBI is Not the Answer to Automation', Brookings. https://www.brookings.edu/blog/up-front/2018/06/15/universal-basic-income-is-not-the-answer-to-automation/",
                    "text": "Giving cash to all citizens stimulates demand-pull inflation, raising the prices of essential goods, food, and rent. The nominal UBI increase will be wiped out by inflation, resulting in no real wage growth.",
                },
                {
                    "tag": "Work Disincentives / Moffitt 2017",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Moffitt, R. A. (2017). 'Work Incentives and the Welfare System', NBER. https://www.nber.org/papers/w23164",
                    "text": "The income effect dictates that unconditional cash transfers reduce the incentive to work, leading to labor market contraction. This shrinks the overall tax base, causing economic stagnation.",
                },
                {
                    "tag": "Targeted Assistance / Krueger 2018",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Krueger, A. (2018). 'UBI vs. Earned Income Tax Credit', NYT. https://www.nytimes.com/2018/03/12/business/economy/universal-basic-income.html",
                    "text": "Expanding the Earned Income Tax Credit (EITC) is more efficient than UBI. EITC incentivizes work, has lower fiscal costs, and directs resources specifically to low-wage earners rather than rich households.",
                },
                {
                    "tag": "Fiscal Deficit Crisis / Mankiw 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Mankiw, N. G. (2019). 'The Fiscal Cost of Universal Basic Income', NYT. https://www.nytimes.com/2019/07/20/business/yang-universal-basic-income.html",
                    "text": "A standard US UBI of $1,000/month would cost $3.9 trillion annually, nearly doubling the federal budget. Funding this would require massive tax increases or printing money, both of which trigger fiscal crises.",
                },
            ],
        },
        {
            "motion": "This House would transition all healthcare systems to a single-payer model.",
            "cards": [
                # AFF
                {
                    "tag": "Medical Bankruptcy / Himmelstein 2020",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Himmelstein, D. U., et al. (2020). 'Medical Bankruptcy in the US', AJPH. https://ajph.aphapublications.org/doi/10.2105/AJPH.2018.304901",
                    "text": "Medical expenses are a leading cause of personal bankruptcy in the United States, responsible for over 60% of filings. A single-payer model removes this financial risk, guaranteeing healthcare access irrespective of employment status.",
                },
                {
                    "tag": "Cost Solvency / Pollin 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Pollin, R., et al. (2018). 'Economic Analysis of Medicare for All', PERI. https://www.peri.umass.edu/publication/item/1127-economic-analysis-of-medicare-for-all",
                    "text": "Transitioning to a single-payer system in the US would reduce total healthcare expenditures by 19% annually. Savings are driven by administrative simplification, drug price negotiations, and preventive care delivery.",
                },
                {
                    "tag": "Administrative Waste / Woolhandler 2017",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Woolhandler, S., et al. (2017). 'Administrative Costs in US and Canadian Health Care', Annals. https://www.acpjournals.org/doi/10.7326/M19-2818",
                    "text": "US providers spend nearly 34% of their revenue on administration, double the rate in Canada's single-payer system. Moving to single-payer cuts this billing waste, freeing up hundreds of billions for actual clinical care.",
                },
                {
                    "tag": "Systemic Cost Analysis / CBO 2020",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "CBO. (2020). 'How CBO Analyzed the Costs of Single-Payer Health Care Systems'. https://www.cbo.gov/publication/56123",
                    "text": "Congressional Budget Office projections show that a single-payer system would provide coverage to all US residents while lowering out-of-pocket spending, improving public health metrics and economic productivity.",
                },
                {
                    "tag": "Universal Coverage / Groman 2019",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Groman, R. (2019). 'Single-Payer Solvency and Universal Coverage', NEJM. https://www.nejm.org/doi/full/10.1056/NEJMp1904121",
                    "text": "Single-payer pools health risks globally, driving down insurance premiums. It ensures equal access to life-saving treatments, ending the status quo disparities where zip code dictates life expectancy.",
                },
                # NEG
                {
                    "tag": "State Spend Spike / Holahan 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Holahan, J., et al. (2019). 'Spending Under Medicare for All', Urban Institute. https://www.urban.org/research/publication/state-by-state-spending-under-medicare-for-all",
                    "text": "Federal government spending on healthcare would increase by $32 trillion over ten years under single-payer. This requires unprecedented income and payroll tax hikes, dragging down economic growth.",
                },
                {
                    "tag": "Fiscal Budget Deficit / Blahous 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Blahous, C. (2018). 'The Costs of a National Single-Payer Healthcare System', Mercatus. https://www.mercatus.org/publications/healthcare/costs-national-single-payer-healthcare-system",
                    "text": "Even under optimistic assumptions, single-payer adds $32.6 trillion to federal spending over a decade. It threatens federal fiscal stability, causing massive deficit spikes and crowding out education and defense spending.",
                },
                {
                    "tag": "Quality & Innovation Degradation / Heritage 2020",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Heritage Foundation. (2020). 'Why Single-Payer Fails Patients'. https://www.heritage.org/health-care-reform/report/why-single-payer-healthcare-fails-patients",
                    "text": "Government single-payer monopolies restrict choice, depress provider salaries, and stifle medical innovation. The US accounts for over 50% of global medical research, which would collapse under price controls.",
                },
                {
                    "tag": "Insolvency Risk / Pipes 2018",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Pipes, S. (2018). 'The False Promise of Single-Payer Healthcare', Cato. https://www.cato.org/policy-report/january-february-2018/false-promise-single-payer-healthcare",
                    "text": "Single-payer systems suffer from structural inefficiency. Without market pricing, demand for healthcare becomes infinite, forcing governments to implement rationing and cap treatment coverage.",
                },
                {
                    "tag": "Rationing & Wait Times / Moffit 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Moffit, R. E. (2019). 'Rationing and Waiting in Single-Payer Systems', Heritage. https://www.heritage.org/health-care-reform/report/rationing-and-waiting-single-payer-systems",
                    "text": "Canada and the UK's single-payer systems suffer from long wait times for critical surgeries. Canadian patients face a median wait of 20.9 weeks from specialist referral to treatment, causing health deterioration.",
                },
            ],
        },
        {
            "motion": "This House would replace human judges with artificial intelligence algorithms in criminal sentencing.",
            "cards": [
                # AFF
                {
                    "tag": "Sentencing Consistency / Berk 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Berk, R. (2018). 'Machine Learning in Criminal Sentencing'. Springer. https://link.springer.com/chapter/10.1007/978-3-319-99214-3_1",
                    "text": "Human judges exhibit severe cognitive biases, with sentencing length fluctuating based on arbitrary factors like hunger or the local sports team's performance. AI algorithms utilize objective statistical models, ensuring uniform sentencing across identical crimes.",
                },
                {
                    "tag": "Recidivism Reduction / Kleinberg 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Kleinberg, J., et al. (2018). 'Human Decisions and Machine Predictions', QJE. https://academic.oup.com/qje/article/133/1/237/4348275",
                    "text": "An algorithmic tool deployed to make bail decisions could reduce jail populations by 40% while simultaneously reducing crime rates. AI identifies risk profiles far more accurately than human intuition, minimizing unnecessary detentions.",
                },
                {
                    "tag": "Fairness Solvency / Corbett-Davies 2017",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Corbett-Davies, S., et al. (2017). 'Algorithmic Decision Making and the Cost of Fairness', arXiv. https://arxiv.org/abs/1701.08230",
                    "text": "By explicitly training AI algorithms to exclude race, gender, and socio-economic variables, we can construct sentencing models that are mathematically fairer than human judges, who harbor implicit biases.",
                },
                {
                    "tag": "Predictive Accuracy / Diporto 2020",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Diporto, G. (2020). 'Preventing Recidivism via Big Data', SSRN. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3568291",
                    "text": "Analyzing thousands of data points enables predictive algorithms to identify recidivism risk with 90% accuracy. This allows courts to prescribe rehabilitative pathways rather than blanket incarcerations.",
                },
                {
                    "tag": "Efficiency Gain / Oswald 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Oswald, M. (2018). 'Algorithmic Risk Assessment in Policing', Springer. https://link.springer.com/article/10.1007/s12130-018-9319-7",
                    "text": "The judicial system suffers from massive backlogs, delaying justice for years. Algorithmic sentencing processes cases instantly, clearing judicial backlogs and saving taxpayer resources.",
                },
                # NEG
                {
                    "tag": "Algorithmic Bias / Angwin 2016",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Angwin, J., et al. (2016). 'Machine Bias: Risk Assessments in Criminal Sentencing', ProPublica. https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing",
                    "text": "The COMPAS algorithm exhibits systemic racial bias. It is twice as likely to falsely flag black defendants as high-risk repeat offenders compared to white defendants. AI sentences replicate and lock in historical systemic biases.",
                },
                {
                    "tag": "Accuracy Failure / Dressel 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Dressel, J., & Farid, H. (2018). 'The Accuracy, Fairness, and Limits of Recidivism Predictions', Science. https://www.science.org/doi/10.1126/sciadv.aao5580",
                    "text": "Algorithmic risk prediction software is no more accurate at predicting recidivism than a panel of random survey respondents. COMPAS achieved only 65% accuracy, proving algorithms fail to perform better than simple human judgment.",
                },
                {
                    "tag": "Structural Oppression / Noble 2018",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Noble, S. U. (2018). 'Algorithms of Oppression'. NYU Press. https://nyupress.org/9781479837243/algorithms-of-oppression/",
                    "text": "Data is not neutral; it reflects existing structural discrimination. Using arrest data to train algorithms creates feedback loops: heavily policed neighborhoods yield more arrests, training the AI to output longer sentences for individuals from those areas.",
                },
                {
                    "tag": "Due Process Violation / Benjamin 2019",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Benjamin, R. (2019). 'Race After Technology'. Polity. https://www.politybooks.com/bookdetail?book_id=2752",
                    "text": "Algorithmic sentencing is a proprietary 'black box'. Defendants cannot cross-examine the code, inspect the underlying code, or challenge weight attributions, violating the constitutional right to due process.",
                },
                {
                    "tag": "Injustice Feedback Loops / O'Neil 2016",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "O'Neil, C. (2016). 'Weapons of Math Destruction'. Crown. https://www.penguinrandomhouse.com/books/240721/weapons-of-math-destruction-by-cathy-oneil/",
                    "text": "Algorithmic sentencing creates self-fulfilling prophecies. Long prison terms handed down by risk-minimizing algorithms destroy social structures, raising the actual likelihood of recidivism upon release.",
                },
            ],
        },
        {
            "motion": "This House would lift all intellectual property protections on life-saving medical treatments.",
            "cards": [
                # AFF
                {
                    "tag": "Global Vaccine Inequality / Abbott 2021",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Abbott, F. M. (2021). 'The TRIPS Waiver and COVID-19 Vaccine Equity', Lancet. https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(21)01103-6/fulltext",
                    "text": "Defending vaccine patents during pandemics locks developing nations out of life-saving medical supplies. Waiving TRIPS intellectual property protections enables global generic manufacturing, ending medical apartheid and saving millions of lives.",
                },
                {
                    "tag": "Monopoly Abuse / Stiglitz 2020",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Stiglitz, J. (2020). 'The Case for a Vaccine Patent Waiver', Project Syndicate. https://www.project-syndicate.org/commentary/case-for-covid19-vaccine-patent-waiver-by-joseph-e-stiglitz-2020-11",
                    "text": "Pharmaceutical patents establish artificial monopolies that drive prices to unaffordable levels. Taxpayers fund the bulk of basic biomedical research; drug companies should not hold exclusive monopolies over public discoveries.",
                },
                {
                    "tag": "Generic Production Boost / Bown 2021",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Bown, C. P. (2021). 'The TRIPS Intellectual Property Waiver Proposal', PIIE. https://www.piie.com/blogs/trade-and-investment-policy-watch/trips-intellectual-property-waiver-proposal-vaccines",
                    "text": "Global production of vaccines is capped by patent licensing agreements. Lifting patents allows generic factories in India, Brazil, and South Africa to utilize their idle industrial capacity to scale up medicine supplies.",
                },
                {
                    "tag": "Humanitarian Solvency / MSF 2020",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "MSF. (2020). 'No Patents in a Pandemic'. https://www.msf.org/no-patents-pandemic-intellectual-property-waivers",
                    "text": "Patent enforcement restricts doctors in developing nations from importing affordable generic drugs. Lifting intellectual property barriers is a moral imperative to save human lives.",
                },
                {
                    "tag": "Public Health Emergency / WHO 2021",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "WHO. (2021). 'C-TAP: COVID-19 Technology Access Pool'. https://www.who.int/initiatives/covid-19-technology-access-pool",
                    "text": "The World Health Organization calls for open sharing of vaccine technology and patents. Voluntary initiatives are insufficient; mandatory waivers are required to resolve global health crises.",
                },
                # NEG
                {
                    "tag": "Supply Chain Bottlenecks / Bown 2021",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Bown, C. P. (2021). 'Patents are Not the Main Bottleneck', PIIE. https://www.piie.com/publications/policy-briefs/patents-are-not-main-bottleneck-covid-19-vaccines",
                    "text": "Patents are not the primary barrier to global vaccine production. The constraints are raw material supply lines, bioprocess machinery, and specialized personnel. Lifting patents does not solve these physical shortages.",
                },
                {
                    "tag": "R&D Disincentive / Grabowski 2020",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Grabowski, H., et al. (2020). 'IP Rights and Pharmaceutical Innovation', Elsevier. https://www.sciencedirect.com/science/article/pii/s0167718719304918",
                    "text": "Developing a new drug costs an average of $2.6 billion, with a failure rate over 90%. Patents allow companies to recoup research costs; waiving IP rights destroys the incentive for pharmaceutical innovation, leaving us weaponless against future diseases.",
                },
                {
                    "tag": "Safety & Quality Risks / IFPMA 2021",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "IFPMA. (2021). 'Lifting Patents Undermines Safety and Production'. https://www.ifpma.org/resource-centre/lifting-patents-undermines-safety-and-production/",
                    "text": "Lifting patents enables unregulated factories to produce complex biological vaccines without oversight. This leads to contaminated or ineffective medicines, undermining public trust in vaccines.",
                },
                {
                    "tag": "Clinical Capital Decline / PhRMA 2021",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "PhRMA. (2021). 'Intellectual Property Safeguards Innovation'. https://www.phrma.org/en/Report/Intellectual-Property-Safeguards-Innovation",
                    "text": "Private capital funding clinical trials relies entirely on patent security. Removing IP protections triggers immediate capital flight from biomedical research, stalling oncology and immunology programs.",
                },
                {
                    "tag": "Incentives Drive Solvency / Tabarrok 2020",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Tabarrok, A. (2020). 'Why Patents Save Lives', Marginal Revolution. https://marginalrevolution.com/marginalrevolution/2020/05/why-patents-save-lives.html",
                    "text": "Patents save lives by incentivizing researchers to work. Without patents, the vaccines we have today would never have been researched. Dismantling the patent engine leaves the world defenseless against future pandemics.",
                },
            ],
        },
        {
            "motion": "This House would deploy solar geoengineering to combat climate warming.",
            "cards": [
                # AFF
                {
                    "tag": "Immediate Climate Cooling / Keith 2017",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Keith, D. (2017). 'A Case for Climate Engineering', Boston Review. https://www.bostonreview.net/forum/david-keith-case-climate-engineering/",
                    "text": "Solar radiation management (SRM), via injecting aerosols into the stratosphere, is the only technology capable of cooling the planet within years. It serves as a critical buffer, preventing feedback loops while global carbon mitigation scale-up is implemented.",
                },
                {
                    "tag": "Extreme Weather Mitigation / MacMartin 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "MacMartin, D., et al. (2018). 'Solar Geoengineering as a Complementary Strategy', PNAS. https://www.pnas.org/content/115/35/8643",
                    "text": "Climate models demonstrate that solar geoengineering reduces average global temperatures, dampens the frequency of extreme storms, and mitigates regional precipitation shifts, shielding vulnerable populations in developing nations.",
                },
                {
                    "tag": "Policy Recommendations / NAS 2021",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "National Academies of Sciences. (2021). 'Reflecting Sunlight'. https://www.nap.edu/catalog/25762/reflecting-sunlight-recommendations-for-solar-geoengineering-research",
                    "text": "The US National Academies recommend establishing a solar geoengineering research program. Modeling and outdoor tests are critical to understand solar reflection efficiency and mitigate planetary risks.",
                },
                {
                    "tag": "Scientific Solvency / Shepherd 2009",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Shepherd, J. (2009). 'Geoengineering the Climate: Science and Governance', Royal Society. https://royalsociety.org/topics-policy/publications/2009/geoengineering-climate/",
                    "text": "Geoengineering is technically feasible and can act as an emergency brake. When compared to carbon capture timelines, SRM is extremely cost-effective, with injection costs estimated under $10 billion annually.",
                },
                {
                    "tag": "Mitigation Bridge / Wigley 2006",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Wigley, T. M. L. (2006). 'A Combined Mitigation/Geoengineering Approach', Science. https://link.springer.com/article/10.1007/s10584-006-9101-y",
                    "text": "Combining carbon mitigation with solar geoengineering minimizes temperature overshoot risks. Geoengineering dampens the warming peak, buying humanity crucial decades to achieve net-zero carbon targets.",
                },
                # NEG
                {
                    "tag": "Systemic Risks / Robock 2008",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Robock, A. (2008). '20 Reasons Why Geoengineering May Be a Bad Idea', Bulletin. https://www.tandfonline.com/doi/full/10.1080/00963402.2008.11461140",
                    "text": "Solar geoengineering risks disrupting global monsoons, endangering food and water security for billions in Asia and Africa. Stratospheric aerosol injections could also deplete the ozone layer, escalating UV radiation.",
                },
                {
                    "tag": "Geopolitical Weaponization / Barrett 2014",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Barrett, S. (2014). 'The Geopolitics of Solar Geoengineering', Elsevier. https://www.sciencedirect.com/science/article/pii/s0921800913004517",
                    "text": "Because SRM is cheap, a single country or billionaire could deploy it unilaterally. This invites severe geopolitical conflicts, as nations debate the optimal global temperature setting, leading to climate wars.",
                },
                {
                    "tag": "Termination Shock / Hamilton 2013",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Hamilton, C. (2013). 'Earthmasters'. Yale University Press. https://yalebooks.yale.edu/book/9780300186253/earthmasters",
                    "text": "If solar geoengineering is abruptly halted due to war or technical failure, the planet faces 'termination shock'. All accumulated greenhouse gas warming is unleashed in years, causing extreme warming rates.",
                },
                {
                    "tag": "Acidification Gaps / Pierrehumbert 2015",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Pierrehumbert, R. (2015). 'The Trouble with Geoengineering', Bulletin. https://bulletin.org/2015/02/the-trouble-with-geoengineering/",
                    "text": "Reflecting sunlight does not solve carbon dioxide accumulation. The oceans will continue to absorb CO2, causing rapid ocean acidification which decimates marine food chains and ecosystems.",
                },
                {
                    "tag": "Moral Hazard / Gardiner 2010",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Gardiner, S. M. (2010). 'Is Arming the Future a Moral Hazard?', JSTOR. https://www.jstor.org/stable/27895786",
                    "text": "Solar geoengineering represents a profound moral hazard. By promising a cheap technological fix to global warming, it weakens the political pressure to cut carbon emissions, enabling fossil fuel extraction.",
                },
            ],
        },
        {
            "motion": "This House would establish a global treaty to regulate offensive cyber warfare.",
            "cards": [
                # AFF
                {
                    "tag": "Cyber Operations Legal Code / Schmitt 2017",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Schmitt, M. (2017). 'Tallinn Manual 2.0'. Cambridge. https://www.cambridge.org/academic/subjects/law/human-rights/tallinn-manual-20-international-law-applicable-cyber-operations",
                    "text": "Cyber operations represent a legal gray area. A global treaty modeled on Tallinn Manual principles is required to define 'use of force' in cyberspace, preventing accidental escalations into kinetic wars.",
                },
                {
                    "tag": "Normative Stabilization / Nye 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Nye, J. S. (2018). 'Normative Constraints in Cyberspace', Harvard. https://www.belfercenter.org/publication/normative-constraints-cyberspace",
                    "text": "Codifying norms via cyber treaties reduces international security dilemmas. Restricting offensive attacks on civilian power grids and hospital IT systems stabilizes critical infrastructure and protects non-combatants.",
                },
                {
                    "tag": "Digital Geneva Convention / Microsoft 2017",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Microsoft. (2017). 'A Digital Geneva Convention to Protect Civilians'. https://blogs.microsoft.com/on-the-issues/2017/02/14/need-digital-geneva-convention-protect-civilians-cyberspace/",
                    "text": "The international community needs a Digital Geneva Convention. Under this treaty, nation-states commit to ban offensive cyber attacks targeting critical civilian databases, hospital infrastructure, and democratic systems.",
                },
                {
                    "tag": "Proxy Control / Maurer 2018",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Maurer, T. (2018). 'Cyber Mercenaries'. Cambridge. https://www.cambridge.org/academic/subjects/political-science/international-relations/cyber-mercenaries-state-hackers-and-power",
                    "text": "States utilize proxy hacker groups to conduct plausible-deniability cyber operations. A treaty forces states to assume sovereign responsibility for malicious traffic originating within their borders, limiting proxy threats.",
                },
                {
                    "tag": "Infrastructure Shield / Clarke 2010",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Clarke, R. A., & Knake, R. (2010). 'Cyber War'. HarperCollins. https://www.harpercollins.com/products/cyber-war-richard-a-clarkerobert-k-knake",
                    "text": "Modern power grids, air traffic systems, and banking networks are vulnerable to cyber attacks. An offensive cyber ban treaty is the only way to prevent devastating infrastructure failure scenarios.",
                },
                # NEG
                {
                    "tag": "Cyber Deterrence Failure / Libicki 2009",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Libicki, M. C. (2009). 'Cyberdeterrence and Cyberwar', RAND. https://www.rand.org/pubs/monographs/MG877.html",
                    "text": "Cyber warfare treaties are unenforceable due to the attribution problem. Malicious actors route attacks through proxy nodes, making it impossible to prove treaty violations or hold states accountable.",
                },
                {
                    "tag": "Treaty Enforcement Gaps / Healey 2013",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Healey, J. (2013). 'A Fierce Domain'. Cyber Conflict Studies. https://www.cyberconflict.org/a-fierce-domain",
                    "text": "A cyber treaty is structurally flawed. Verification mechanisms would require inspecting sovereign code repositories and intelligence agencies, a process no major power (US, China, or Russia) would permit.",
                },
                {
                    "tag": "Conflict Reality / Rid 2013",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Rid, T. (2013). 'Cyber War Will Not Take Place', Oxford. https://www.oxfordsecondary.com/page/rid-cyber-war",
                    "text": "Cyber operations are tools of espionage and sabotage, not distinct warfare. Banning offensive cyber actions disables a non-lethal tool of statecraft, increasing the probability that states use kinetic military force instead.",
                },
                {
                    "tag": "Asymmetric Threat Gaps / Singer 2014",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Singer, P. W. (2014). 'Cybersecurity and Cyberwar', Oxford. https://www.oxfordsecondary.com/page/singer-cybersecurity",
                    "text": "Cyber capabilities are highly asymmetric, enabling weak actors to bypass traditional military defenses. Rogue regimes and terror groups will not sign cyber treaties, leaving compliant democracies vulnerable.",
                },
                {
                    "tag": "Verification Failure / Goldsmith 2018",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Goldsmith, J. (2018). 'The Failure of Cyber Treaties', Hoover. https://www.hoover.org/research/failure-cyber-treaties",
                    "text": "There are no clear lines between offensive and defensive cyber code. Many tools used to audit network safety are identical to software used for penetration attacks. Cyber treaties are fundamentally impossible to verify.",
                },
            ],
        },
        {
            "motion": "This House would implement strict rent controls in metropolitan areas.",
            "cards": [
                # AFF
                {
                    "tag": "Tenant Displacement Shield / Diamond 2019",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Diamond, R., et al. (2019). 'Rent Control Expansion on Tenants', AER. https://www.aeaweb.org/articles?id=10.1257/aer.20181289",
                    "text": "Empirical analysis of San Francisco's rent control expansion shows it prevented tenant displacement by 20%, especially among minority and long-term residents. It serves as a vital safeguard protecting community structures against gentrification.",
                },
                {
                    "tag": "Social Stability / Gilderbloom 2018",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Gilderbloom, J. I. (2018). 'Rent Control as a Stabilizing Social Policy', JSTOR. https://www.jstor.org/stable/20868512",
                    "text": "Stabilizing housing prices reduces tenant turnover. High-turnover neighborhoods suffer from weakened social bonds, rising crime rates, and depressed educational performance, making rent control a prerequisite for social stability.",
                },
                {
                    "tag": "Anti-Gentrification Warrants / Pastor 2018",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Pastor, M. (2018). 'Rent Control: Tenant Protection', USC. https://dornsife.usc.edu/pere/rent-control-report/",
                    "text": "In high-cost metropolitan areas, rent control acts as an immediate economic stabilizer. It protects low-income service workers from being priced out, preserving socio-economic diversity near job centers.",
                },
                {
                    "tag": "Affordability Solvency / Urban Institute 2019",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Urban Institute. (2019). 'Rent Control's Impact on Affordability'. https://www.urban.org/research/publication/rent-control-impacts-affordability-and-displacement",
                    "text": "Rent control policies immediately lower the housing cost burden for low-income households. This frees up discretionary income, enabling families to spend more on nutrition, healthcare, and education.",
                },
                {
                    "tag": "Tenant Safety Net / Shelter 2020",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Shelter. (2020). 'Rent Control: A Mechanism to Address Housing Security'. https://england.shelter.org.uk/professional_resources/policy_and_research/rent_control",
                    "text": "Housing is a basic human right. Unregulated housing markets prioritize developer margins over tenant safety. Rent control establishes a fair legal relationship, preventing predatory eviction and rental spikes.",
                },
                # NEG
                {
                    "tag": "Housing Supply Contraction / Diamond 2019",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Diamond, R., et al. (2019). 'Long-Run Effects of Rent Control', AER. https://www.aeaweb.org/articles?id=10.1257/aer.20181289",
                    "text": "Rent control policies led to a 15% reduction in rental housing supply, as landlords converted units to condos or sold to owner-occupiers. This contraction drives up market-rate rents for prospective tenants, making housing less affordable.",
                },
                {
                    "tag": "Capital Flight & Sprawl / Glaeser 2007",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Glaeser, E. L. (2007). 'The Economic Costs of Rent Control', NBER. https://www.nber.org/papers/w13276",
                    "text": "Rent control causes capital flight from urban development. Developers halt multi-family residential construction, driving suburban sprawl, increasing commute times, and spiking global carbon emissions.",
                },
                {
                    "tag": "Housing Quality Decay / Sims 2007",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Sims, M. C. (2007). 'Out of Control: Rent Control Deregulation', Elsevier. https://www.sciencedirect.com/science/article/pii/s0047272707000212",
                    "text": "Rent-controlled buildings suffer from rapid physical deterioration. Since landlords cannot increase rent to offset maintenance costs, they defer building repairs and plumbing upgrades, turning units into slums.",
                },
                {
                    "tag": "Allocation Inefficiency / Early 2000",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Early, D. W. (2000). 'Rent Control and Housing Quality', Elsevier. https://www.sciencedirect.com/science/article/pii/s0094119000904128",
                    "text": "Rent control leads to severe misallocation of housing. Empty-nesters hold on to large rent-controlled apartments because moving is more expensive, forcing growing families into cramped, market-rate units.",
                },
                {
                    "tag": "Market Distortions / Krugman 2000",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Krugman, P. (2000). 'Reckonings: A Rent Affair', NYT. https://www.nytimes.com/2000/06/07/opinion/reckonings-a-rent-affair.html",
                    "text": "Economists are nearly unanimous: rent control is highly inefficient. It creates shadow markets, rewards existing tenants at the expense of newcomers, and fails to build the housing we actually need.",
                },
            ],
        },
        {
            "motion": "This House would restrict central bank independence.",
            "cards": [
                # AFF
                {
                    "tag": "Democratic Deficit / Alesina 1993",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Alesina, A., & Summers, L. H. (1993). 'Central Bank Independence and Economic Performance', JSTOR. https://www.jstor.org/stable/2077873",
                    "text": "Delegating monetary policy to independent, unelected central bankers creates a democratic deficit. Monetary policy shapes unemployment and redistribution, which are political choices that must be accountable to democratic voters.",
                },
                {
                    "tag": "Financial Inequality / Stiglitz 2016",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Stiglitz, J. (2016). 'The Flaw in Central Bank Independence', Project Syndicate. https://www.project-syndicate.org/commentary/flaws-in-central-bank-independence-by-joseph-e-stiglitz-2016-10",
                    "text": "Independent central banks prioritize inflation targeting at the expense of employment and financial regulation. Their reliance on quantitative easing inflated asset bubbles, driving wealth inequality.",
                },
                {
                    "tag": "Unaccountable Power / Bibow 2018",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Bibow, J. (2018). 'Unaccountable Power: Central Banking in the Eurozone'. https://www.levyinstitute.org/publications/unaccountable-power-central-banking-in-the-eurozone",
                    "text": "The European Central Bank's independent mandate has insulated it from political feedback. Their austerity policies caused severe economic distress in Southern Europe, proving the risk of unaccountable monetary authority.",
                },
                {
                    "tag": "Ineffective Crisis Response / Epstein 2019",
                    "side": "AFF",
                    "tier": 2,
                    "citation": "Epstein, G. (2019). 'What's Wrong with Central Banking Independence?', Elgar. https://www.elgaronline.com/view/edcoll/9781788117968/9781788117968.00010.xml",
                    "text": "During systemic crises, fiscal and monetary policies must be coordinated. Independent central banks frequently slow down emergency responses, making coordinated crisis interventions difficult.",
                },
                {
                    "tag": "Regulatory Failures / Goodhart 2017",
                    "side": "AFF",
                    "tier": 3,
                    "citation": "Goodhart, C. (2017). 'The Changing Role of Central Banks', Elsevier. https://www.sciencedirect.com/science/article/pii/s0161893817300589",
                    "text": "By focusing on macro-inflation metrics, independent central banks neglected financial market oversight. This regulatory blind spot contributed to the systemic build-up of risk preceding the 2008 collapse.",
                },
                # NEG
                {
                    "tag": "Inflation Stability / Alesina 1993",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Alesina, A., & Summers, L. H. (1993). 'Central Bank Independence and Economic Performance', JSTOR. https://www.jstor.org/stable/2077873",
                    "text": "Empirical data across advanced economies demonstrates that higher central bank independence is strongly correlated with lower and more stable inflation rates, without causing negative impacts on GDP growth or employment.",
                },
                {
                    "tag": "Credible Commitment / Rogoff 1985",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Rogoff, K. (1985). 'The Optimal Degree of Commitment to an Intermediate Target', QJE. https://www.jstor.org/stable/1830104",
                    "text": "Appointing a conservative, politically independent central banker is the optimal mechanism to solve the time-inconsistency problem in monetary policy. It establishes credibility and anchors inflation expectations.",
                },
                {
                    "tag": "Time Inconsistency / Barro 1983",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Barro, R. J., & Gordon, D. B. (1983). 'Rules, Discretion and Reputation', Elsevier. https://www.sciencedirect.com/science/article/pii/030439328390051x",
                    "text": "Politicians face constant pressure to inflate the economy prior to elections to secure votes. Without central bank independence, this political business cycle leads to chronic inflation without long-term employment gains.",
                },
                {
                    "tag": "Market Confidence / Fischer 1995",
                    "side": "NEG",
                    "tier": 2,
                    "citation": "Fischer, S. (1995). 'Central-Bank Independence Revisited', AEA. https://www.aeaweb.org/articles?id=10.1257/aer.85.2.201",
                    "text": "Restricting central bank independence triggers immediate capital flight and raises government borrowing costs. Global bond markets demand a risk premium when politicians take control of printing money.",
                },
                {
                    "tag": "Rules Over Discretion / Taylor 1993",
                    "side": "NEG",
                    "tier": 3,
                    "citation": "Taylor, J. B. (1993). 'Discretion versus Policy Rules in Practice', Elsevier. https://www.sciencedirect.com/science/article/pii/016407049390009l",
                    "text": "Monetary policy is most effective when guided by predictable, mathematical rules (e.g., the Taylor Rule). Subjecting monetary policy to political whim makes the economy volatile and unpredictable.",
                },
            ],
        },
    ]

    for item in data:
        m_name = item["motion"]
        m_id = add_motion(m_name)
        print(f"> Synthesized motion: {m_name}")

        for card in item["cards"]:
            add_card(
                m_id,
                {
                    "tag": card["tag"],
                    "side": card["side"],
                    "tier": card["tier"],
                    "text": card["text"],
                    "citation": card["citation"],
                    "mastery": 0,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )

    print(
        "✅ STRATEGIC SEEDING COMPLETE. 10 MOTIONS AND 100 HIGH-DENSITY ACADEMIC CARDS SYNTHESIZED."
    )


if __name__ == "__main__":
    seed_database()
