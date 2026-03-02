# Thread: On/Off/Non-Contract Analysis
_Exported 8 message(s)_

---
## Message 1
**From:** Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>  
**Date:** Thu 2026-02-12 8:48 PM UTC  
**Subject:** On/Off/Non-Contract Analysis  
**To:** Garrett, Jordan <Jordan_Garrett@PremierInc.com>, Hall, Brian <Brian_Hall@PremierInc.com>, Lilly, Zach <Zach_Lilly@PremierInc.com>, Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>  

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).

Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)

Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available

Who would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 2
**From:** Hall, Brian <Brian_Hall@PremierInc.com>  
**Date:** Thu 2026-02-12 9:46 PM UTC  
**Subject:** Re: On/Off/Non-Contract Analysis  
**To:** Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Garrett, Jordan <Jordan_Garrett@PremierInc.com>, Lilly, Zach <Zach_Lilly@PremierInc.com>, Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>, Schneider, Justin <Justin_Schneider@premierinc.com>, Ralph, Joan <Joan_Ralph@PremierInc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>  

Matt -

Adding @Schneider, Justin and @Ralph, Joan to provide insights for their areas into this model around contract coverage.  I agree RX wholesaler data is probably the right method for pharmacy as a proxy, however I am not sure how much of the food data we have access to inhouse vs getting it from US Foods and other sources.

Justin and Joan - please note the time sensitive nature of this and ideally needing your feedback by tomorrow so the team has a couple days to work through any iterations that may be needed before delivering to Bruce next Thursday.  Feel free to ping me if you have additional questions.

Thanks,
Brian

Brian Hall, MBA, CMRP, MCP, MCAD
Vice President – Strategic Sourcing Operations and Analytics
Supply Chain Services
Office: 704.816.5528
brian_hall@premierinc.com | Premier, Inc. (NASDAQ: PINC)

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 3:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis 

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).

Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)

Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available

Who would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 3
**From:** Garrett, Jordan <Jordan_Garrett@PremierInc.com>  
**Date:** Thu 2026-02-12 10:12 PM UTC  
**Subject:** Re: On/Off/Non-Contract Analysis  
**To:** Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Hall, Brian <Brian_Hall@PremierInc.com>, Lilly, Zach <Zach_Lilly@PremierInc.com>, Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>  

Hi Matt, 

Regarding the definitions, below is my feedback. 

For confirmation, the definitions I believe we’re using are:
On Contract: spend directly tied to an existing Premier contract. (I agree)

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available). (I think this Off Contract should have two components for us to breakout - not sure of naming/titling.

First, is when a Member has spend with a Premier-contracted Supplier in the same Category, but where the Member spend is not going through our Premier contract for some reason.
Second is when we have a contract in the category but the Member is using a non-Premier-contracted supplier.).
The first component of this is stuff we should more easily be going after because (a) it could be that a Member inadvertently did not activate or complete a PMDF, (b) the Member chose to go through another GPO or Direct for some reason, or (c) the supplier is not reporting/paying to Premier when they should inadvertently or intentionally.
The second scenario can take more effort as it involves Member conversions, which can be complex, and oftentimes having to wait months or years for their incumbent contract to expire (if they don't have a w/out Cause termination right).  
Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available. (I agree)
Thanks, 

Jordan Garrett

Senior Director, Digital Health Supplier Engagement

Supplier Engagement | Premier Inc.

M 512.694.9730

premierinc.com

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 2:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis  

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).

Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)

Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available

Who would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 4
**From:** Ralph, Joan <Joan_Ralph@PremierInc.com>  
**Date:** Thu 2026-02-12 11:53 PM UTC  
**Subject:** Re: On/Off/Non-Contract Analysis  
**To:** Hall, Brian <Brian_Hall@PremierInc.com>, Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Garrett, Jordan <Jordan_Garrett@PremierInc.com>, Lilly, Zach <Zach_Lilly@PremierInc.com>, Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>, Schneider, Justin <Justin_Schneider@premierinc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>, Lough, Robert <Bob_Lough@PremierInc.com>  

Get with Bob Lough from my team - he can get you what we need.

Sent from my Verizon, Samsung Galaxy smartphone
Get Outlook for Android
From: Hall, Brian <Brian_Hall@PremierInc.com>
Sent: Thursday, February 12, 2026 3:46:24 PM
To: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>; Schneider, Justin <Justin_Schneider@premierinc.com>; Ralph, Joan <Joan_Ralph@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis  

Matt -

Adding @Schneider, Justin and @Ralph, Joan to provide insights for their areas into this model around contract coverage.  I agree RX wholesaler data is probably the right method for pharmacy as a proxy, however I am not sure how much of the food data we have access to inhouse vs getting it from US Foods and other sources.

Justin and Joan - please note the time sensitive nature of this and ideally needing your feedback by tomorrow so the team has a couple days to work through any iterations that may be needed before delivering to Bruce next Thursday.  Feel free to ping me if you have additional questions.

Thanks,
Brian

Brian Hall, MBA, CMRP, MCP, MCAD
Vice President – Strategic Sourcing Operations and Analytics
Supply Chain Services
Office: 704.816.5528
brian_hall@premierinc.com | Premier, Inc. (NASDAQ: PINC)

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 3:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis  

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).

Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)

Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available

Who would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 5
**From:** Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>  
**Date:** Fri 2026-02-13 12:12 AM UTC  
**Subject:** Re: On/Off/Non-Contract Analysis  
**To:** Garrett, Jordan <Jordan_Garrett@PremierInc.com>, Hall, Brian <Brian_Hall@PremierInc.com>, Lilly, Zach <Zach_Lilly@PremierInc.com>, Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>  

That's an interesting and useful breakout that I hadn't considered. What you're articulating, I often associate more with the concept of being "connected" to a contract rather than being on or off contract, but it's a useful distinction nonetheless. Also, the breakout of the non-contracted spend that Brian articulated, I think, is helpful as well. Both of these are perhaps more detailed in the top level that leadership wants to start with, so maybe it's a two-level hierarchy/drill we create (3 buckets break into 5-6 total sub buckets)?

Ultimately, my opinion is less important here than yours and the other SL leads.. Pick the strategy you're most comfortable advocating for (privilege of the product owner!), and let us know how you would like the team to present it. 

Matt

From: Garrett, Jordan <Jordan_Garrett@PremierInc.com>
Sent: Thursday, February 12, 2026 5:12:25 PM
To: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis  

Hi Matt, 

Regarding the definitions, below is my feedback. 

For confirmation, the definitions I believe we’re using are:
On Contract: spend directly tied to an existing Premier contract. (I agree)

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available). (I think this Off Contract should have two components for us to breakout - not sure of naming/titling.

First, is when a Member has spend with a Premier-contracted Supplier in the same Category, but where the Member spend is not going through our Premier contract for some reason.
Second is when we have a contract in the category but the Member is using a non-Premier-contracted supplier.).
The first component of this is stuff we should more easily be going after because (a) it could be that a Member inadvertently did not activate or complete a PMDF, (b) the Member chose to go through another GPO or Direct for some reason, or (c) the supplier is not reporting/paying to Premier when they should inadvertently or intentionally.
The second scenario can take more effort as it involves Member conversions, which can be complex, and oftentimes having to wait months or years for their incumbent contract to expire (if they don't have a w/out Cause termination right).  
Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available. (I agree)
Thanks, 

Jordan Garrett

Senior Director, Digital Health Supplier Engagement

Supplier Engagement | Premier Inc.

M 512.694.9730

premierinc.com

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 2:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis  

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).

Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract

Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)

Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available

Who would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 6
**From:** Schneider, Justin <Justin_Schneider@premierinc.com>  
**Date:** Fri 2026-02-13 12:51 PM UTC  
**Subject:** RE: On/Off/Non-Contract Analysis  
**To:** Hall, Brian <Brian_Hall@PremierInc.com>, Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Garrett, Jordan <Jordan_Garrett@premierinc.com>, Lilly, Zach <Zach_Lilly@premierinc.com>, Kapu, UdayKumar <UdayKumar_Kapu@premierinc.com>, Ralph, Joan <Joan_Ralph@PremierInc.com>, Zagorsky, Ed <Ed_Zagorsky@premierinc.com>, Scavo, Shelley <Shelley_Scavo@PremierInc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@premierinc.com>  

Including @Zagorsky, Ed for the Pharmacy data piece. Also, @Scavo, Shelley – as she has the best pulse of Pharmacy data sources. Rx Wholesaler is definitely the primary source, but we also have, separately, 503B data, specialty distributor data, and others. 

 

Ed, Shelley – can you connect with Brian first thing this morning, so we can best represent pharmacy’s contract coverage? 

 

Below for more context. 

 

Justin Schneider, PharmD

Group Vice President, Pharmacy

Premier Inc.

M: 312.636.9651

 

From: Hall, Brian <Brian_Hall@PremierInc.com> 
Sent: Thursday, February 12, 2026 4:46 PM
To: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>; Schneider, Justin <Justin_Schneider@premierinc.com>; Ralph, Joan <Joan_Ralph@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis

 

Matt -

 

Adding @Schneider, Justin and @Ralph, Joan to provide insights for their areas into this model around contract coverage.  I agree RX wholesaler data is probably the right method for pharmacy as a proxy, however I am not sure how much of the food data we have access to inhouse vs getting it from US Foods and other sources.

 

Justin and Joan - please note the time sensitive nature of this and ideally needing your feedback by tomorrow so the team has a couple days to work through any iterations that may be needed before delivering to Bruce next Thursday.  Feel free to ping me if you have additional questions.

 

Thanks,

Brian

 

Brian Hall, MBA, CMRP, MCP, MCAD

Vice President – Strategic Sourcing Operations and Analytics

Supply Chain Services

Office: 704.816.5528

brian_hall@premierinc.com | Premier, Inc. (NASDAQ: PINC)

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 3:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis

 

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contractOff Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is availableWho would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 7
**From:** Hall, Brian <Brian_Hall@PremierInc.com>  
**Date:** Fri 2026-02-13 1:44 PM UTC  
**Subject:** RE: On/Off/Non-Contract Analysis  
**To:** Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Garrett, Jordan <Jordan_Garrett@premierinc.com>, Lilly, Zach <Zach_Lilly@premierinc.com>, Kapu, UdayKumar <UdayKumar_Kapu@premierinc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@premierinc.com>  

I agree with this.  Have a high level red/yellow/green view that Bruce wants but the ability to drill into further subcats certainly helps as that becomes part of how the spend may or may not be addressable.

 

Thanks,

Brian 

 

Brian Hall, MBA, CMRP, MCP, MCAD
Vice President – Strategic Sourcing Operations & Analytics - Supply Chain Services

Office: 704.816.5528 | eFax: 704.733.2062
brian_hall@premierinc.com  |  Premier, Inc. (NASDAQ: PINC)

Sr. Administrative Coordinator:  Melissa Smith  Melissa_Smith@premierinc.com 

 

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com> 
Sent: Friday, February 13, 2026 8:00 AM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis

 

That's an interesting and useful breakout that I hadn't considered. What you're articulating, I often associate more with the concept of being "connected" to a contract rather than being on or off contract, but it's a useful distinction nonetheless. Also, the breakout of the non-contracted spend that Brian articulated, I think, is helpful as well. Both of these are perhaps more detailed in the top level that leadership wants to start with, so maybe it's a two-level hierarchy/drill we create (3 buckets break into 5-6 total sub buckets)?

 

Ultimately, my opinion is less important here than yours and the other SL leads.. Pick the strategy you're most comfortable advocating for (privilege of the product owner!), and let us know how you would like the team to present it. 

 

Matt

From: Garrett, Jordan <Jordan_Garrett@PremierInc.com>
Sent: Thursday, February 12, 2026 5:12:25 PM
To: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis 

 

Hi Matt, 

 

Regarding the definitions, below is my feedback. 

 

For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contract. (I agree)Off Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available). (I think this Off Contract should have two components for us to breakout - not sure of naming/titling.First, is when a Member has spend with a Premier-contracted Supplier in the same Category, but where the Member spend is not going through our Premier contract for some reason.
Second is when we have a contract in the category but the Member is using a non-Premier-contracted supplier.).
The first component of this is stuff we should more easily be going after because (a) it could be that a Member inadvertently did not activate or complete a PMDF, (b) the Member chose to go through another GPO or Direct for some reason, or (c) the supplier is not reporting/paying to Premier when they should inadvertently or intentionally.
The second scenario can take more effort as it involves Member conversions, which can be complex, and oftentimes having to wait months or years for their incumbent contract to expire (if they don't have a w/out Cause termination right).  
Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is available. (I agree)
Thanks, 

 

Jordan Garrett

Senior Director, Digital Health Supplier Engagement

Supplier Engagement | Premier Inc.

M 512.694.9730

premierinc.com

 

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 2:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis 

 

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contractOff Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is availableWho would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt

---
## Message 8
**From:** Scavo, Shelley <Shelley_Scavo@PremierInc.com>  
**Date:** Fri 2026-02-13 1:45 PM UTC  
**Subject:** Re: On/Off/Non-Contract Analysis  
**To:** Schneider, Justin <Justin_Schneider@premierinc.com>, Hall, Brian <Brian_Hall@PremierInc.com>, Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>, Garrett, Jordan <Jordan_Garrett@premierinc.com>, Lilly, Zach <Zach_Lilly@premierinc.com>, Kapu, UdayKumar <UdayKumar_Kapu@premierinc.com>, Ralph, Joan <Joan_Ralph@PremierInc.com>, Zagorsky, Ed <Ed_Zagorsky@premierinc.com>  
**Cc:** Hendrix, Jennie <Jennie_Hendrix@premierinc.com>, Scavo, Shelley <Shelley_Scavo@PremierInc.com>  

Hi Brian and team!  If I've misunderstood the question below, please let me know.

For the Pharmacy wholesaler data, I can confirm the following is used to identify specific 'buckets' of spend.  We use a combination of two attributes to bucket spend: Wholesaler Purchase Type and Premier Award Status.

Wholesaler Purchase Type: Transaction level detail (how the drug was purchased.  P, N, O, B, W).  i.e. designated by the wholesaler per invoice transaction.​
Premier Award Status: Identification on if the NDC/Product is available on Premier contract (for the member's Class of Trade).

Said more simply: 
How did the wholesaler say the transaction was made?
Did we have the item on Premier contract?

On Contract: Where the wholesaler reports spend tied to a Premier contract, where we confirm the NDC/Product is available on Premier Contract
Off Contract: We have two buckets - Off Exact and Off Equivalent
    Off Exact: The wholesaler identifies the member purchased the item NOT using a Premier contract, but the same exact NDC/item purchased is available on Premier Contract
    Off Equivalent: The wholesaler identifies the member purchased the item NOT using a Premier contract, but an equivalent item is available on Premier Contract
Non-Contract: The wholesaler identifies the member purchased the item using No contract, where Premier has no contract available
    
Not categorized as a 'spend type', but wanted to mention a couple of other notable categories:
Other Contract Spend: The wholesaler identifies the member purchased the item using some "other" contract, even where Premier has something available. 

Premier is moving away from "Other" for this and asking wholesalers to provide either:
        Private Contract: Those purchases tied to a Private or Local agreement
        Wholesaler Contract: Those purchases tied to a Wholesaler Source or Other program

We have a few other categories, but for these we do not do any checks against Premier award status.  Essentially, we use whatever the wholesaler provides.
    340B: 340B purchase spend
    WAC: WAC purchase spend
    503B: Items purchased via 503B suppliers (This is all Premier contracted spend today - we get this from admin fee files)
    503A: Items purchased via 503A suppliers (This is all Premier contracted spend today - we get this from admin fee files)

I'm happy to answer any specific questions you have on the pharmacy wholesaler data.  

Thanks, Shelley

Shelley Scavo, MLS (ASCP)
Product Director
GPO Technology & Data Solutions | Premier, Inc. (NASDAQ: PINC)
M.  980.355.1616
shelley_scavo@premierinc.com  

+ Stay Connected: X | LinkedIn | Instagram | Facebook

From: Schneider, Justin <Justin_Schneider@premierinc.com>
Sent: Friday, February 13, 2026 7:51 AM
To: Hall, Brian <Brian_Hall@PremierInc.com>; Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Garrett, Jordan <Jordan_Garrett@premierinc.com>; Lilly, Zach <Zach_Lilly@premierinc.com>; Kapu, UdayKumar <UdayKumar_Kapu@premierinc.com>; Ralph, Joan <Joan_Ralph@PremierInc.com>; Zagorsky, Ed <Ed_Zagorsky@premierinc.com>; Scavo, Shelley <Shelley_Scavo@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@premierinc.com>
Subject: RE: On/Off/Non-Contract Analysis 

Including @Zagorsky, Ed for the Pharmacy data piece. Also, @Scavo, Shelley – as she has the best pulse of Pharmacy data sources. Rx Wholesaler is definitely the primary source, but we also have, separately, 503B data, specialty distributor data, and others.

 

Ed, Shelley – can you connect with Brian first thing this morning, so we can best represent pharmacy’s contract coverage?

 

Below for more context.

 

Justin Schneider, PharmD

Group Vice President, Pharmacy

Premier Inc.

M: 312.636.9651

 

From: Hall, Brian <Brian_Hall@PremierInc.com>
Sent: Thursday, February 12, 2026 4:46 PM
To: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>; Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>; Schneider, Justin <Justin_Schneider@premierinc.com>; Ralph, Joan <Joan_Ralph@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: Re: On/Off/Non-Contract Analysis

 

Matt -

 

Adding @Schneider, Justin and @Ralph, Joan to provide insights for their areas into this model around contract coverage.  I agree RX wholesaler data is probably the right method for pharmacy as a proxy, however I am not sure how much of the food data we have access to inhouse vs getting it from US Foods and other sources.

 

Justin and Joan - please note the time sensitive nature of this and ideally needing your feedback by tomorrow so the team has a couple days to work through any iterations that may be needed before delivering to Bruce next Thursday.  Feel free to ping me if you have additional questions.

 

Thanks,

Brian

 

Brian Hall, MBA, CMRP, MCP, MCAD

Vice President – Strategic Sourcing Operations and Analytics

Supply Chain Services

Office: 704.816.5528

brian_hall@premierinc.com | Premier, Inc. (NASDAQ: PINC)

From: Bossemeyer, Matthew <Matt_Bossemeyer@PremierInc.com>
Sent: Thursday, February 12, 2026 3:48 PM
To: Garrett, Jordan <Jordan_Garrett@PremierInc.com>; Hall, Brian <Brian_Hall@PremierInc.com>; Lilly, Zach <Zach_Lilly@PremierInc.com>; Kapu, UdayKumar <UdayKumar_Kapu@PremierInc.com>
Cc: Hendrix, Jennie <Jennie_Hendrix@PremierInc.com>
Subject: On/Off/Non-Contract Analysis

 

Jordan, Brian,

I meant to bring this up live next week during our regular time, but realized I will be traveling with the family (out next week), and so I hope you don’t mind me sending by email. I’m free tomorrow to connect live as needed.

For the % of spend that is On-Contract vs Off-Contract vs Non-Contract by service line, we’ve realized we can’t credibly produce the Pharma and Food splits from the invoice/AP data alone.

As we dug into the invoices this week, a meaningful share of Rx and Food shows up as large wholesaler/distributor invoices (often aggregated and lacking product/manufacturer detail). That’s not enough granularity to determine contract status the same way we can for Clinical and (increasingly) Non-Clinical using the TSA/line-level views, and unfortunately Rx & Food are not well represented in the TSA, even for a subset of health systems.

Would you mind connecting with your peers in the Pharma (Justin’s team) and Food (Joan’s team) service lines next week to align on how they want to represent contract coverage for their domains—ideally using their existing wholesaler/distributor tracing views/tools?

My impression is that Bill & Bruce are hoping for an initial perspective by next Thursday. Even a first-pass estimate is fine, but it seems preferable to reflect how those teams think about it (versus us try to assess on their behalf).

Specifically, I think what we need to procure/provide for each service line by next Thursday is:

% of total service line spend that is On / Off / Non-Contract (something like the top bar of our wireframe below) + a sentence on methodology/source (e.g., wholesaler tracings, any exclusions).Any known visibility gaps (e.g., what tracings don’t capture vs the “total pie” we’re estimating from invoices).For confirmation, the definitions I believe we’re using are:

On Contract: spend directly tied to an existing Premier contractOff Contract: spend in a category where Premier has a contract, but the spend is off-contract (contracted equivalent available)Non-Contract: spend in a category where Premier does not currently have a contract, or where Premier has a contract but no on-contract equivalent is availableWho would you like delivering the 1st pass update to Bruce & Bill by next Thursday?

If you disagree with the premise (i.e., you think we should derive this credibly on our own), please push back—happy to adjust approach, but we should align quickly either way.

Zach, Uday - your chief objective between now and next Thursday is to support the rest of the team with the updates to the TSA data model necessary to enable them to estimate On / Off / Non-Contract for Clinical and Non-Clinical. We may already be there for Clinical, but for Non-Clinical they will need the subcategorization layered in as well as the flag that identifies which health systems are part of the “fully reporting” cohort (to filter to).

I’ll keep the regularly scheduled time on the calendar for Tuesday as a checkpoint for the team to use as needed.

Thank You,
Matt
