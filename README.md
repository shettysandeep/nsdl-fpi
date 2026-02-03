# FPIs in India

Foreign Portfolio Investors (FPIs) are large foreign institutional investors
like foreign pension funds, etc. and large qualified foreign investors who
invest large sums of money in the Indian capital markets. As of September 2025,
there were 12990 registered FPIs, of which 30% were from the US.

FPIs add significant liquidity and depth to the Indian capital markets. About
17% of the total turnover on NSE in 2025 were due to FPIs - buying and selling
about 18,000 crore shares.

In 2025, we saw FPIs withdrawing over 1.6 lakh crores from the markets - a
catastrophic event if not for the buying by Domestic institutional Investors
(DII) and others, which averted a large correction in the markets. Numerous
factors underlie this level of selling - overvalued, slow down in
earnings, geopolitical risks, tariffs and the stalled US-India trade deal, etc.

NSDL has a large
[dataset](https://www.fpi.nsdl.co.in/web/Reports/ReportsListing.aspx) on FPIs
daily transactions data at the individual stock level. Despite some reporting
issues observed in the data, and the long delay in updating this data (latest
data is from March 2025) this is a largely robust and interesting dataset
with the potential for some interesting insights.

In this repo I extract and clean this dataset towards setting up a Python Shiny app
to enable users to explore. I only look at secondary market transactions in
equities.

The app is [here.]()

I deploy containerizied app on Google cloud.
