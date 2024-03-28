Select 
    Cast([Year] as VarChar(8)) as Year
    ,[Week]
    ,[WeekAmount]
Into #tempdata
 FROM
(
    Select 
        asd.FiscalYear as Year
        ,asd.CalendarWeek as [Week]
        ,sum(ftd.Amount) as [WeekAmount]


        From FinancialTransaction ft
        left Join FinancialTransactionDetail ftd
            on ftd.TransactionId = ft.Id
        left Join FinancialAccount fa
            on fa.Id = ftd.AccountId
        inner join AnalyticsSourceDate asd on convert(date,ft.TransactionDateTime,101) = asd.Date


        where 
            fa.ParentAccountId = 1
            and fa.IsTaxDeductible = 1
            and ftd.amount < 100000
            and TransactionDateTime >= '01/01/{{'Now' | Date:'yyyy' | Minus:5}}'
            and TransactionDateTime < '{{ 'Now' | SundayDate | DateAdd:-6 }}'  -- Remove this line if you want to see giving through the current time.

        Group By asd.FiscalYear,asd.CalendarWeek
) as src;

WITH data_test ([Year],[Week],WeekAmount)
AS (
    Select 'Total' as [Year],[Week],WeekAmount FROM (Select 
        'Total' as [Year]
        ,CalendarWeek as [Week]
        ,sum(ftd.Amount) as WeekAmount

        From FinancialTransaction ft
        left Join FinancialTransactionDetail ftd
            on ftd.TransactionId = ft.Id
        left Join FinancialAccount fa
            on fa.Id = ftd.AccountId
        inner join AnalyticsSourceDate asd on convert(date,ft.TransactionDateTime,101) = asd.Date
        
        where 
            fa.ParentAccountId = 1
            and fa.IsTaxDeductible = 1
            and ftd.amount < 100000
            and TransactionDateTime >= '01/01/{{'Now' | Date:'yyyy' | Minus:5}}'
            and TransactionDateTime < '{{'Now' | Date:'yyyy'}}'  -- Remove this line if you want to see giving through the current time.

        Group By asd.CalendarWeek
       
        ) as src )

Insert into #tempdata
SELECT 'Total',Week,WeekAmount
from data_test
 Order By Week;
 
--WITH data_test ([Year],[Week],WeekAmount)
--AS (
--    Select [Year],[Week],WeekAmount FROM (Select 
--        DatePart(Year,ft.TransactionDateTime) as Year
--        ,FiscalWeek as [Week]
--        ,sum(ftd.Amount) as WeekAmount
--
--        From FinancialTransaction ft
--        inner Join FinancialTransactionDetail ftd
--            on ftd.TransactionId = ft.Id and TransactionDateTime >= '{{'Now' | Date:'01/01/yyyy'}}'
           -- and TransactionDateTime < '01/01/{{'Now' | Date:'yyyy'}}'
--        inner Join FinancialAccount fa
--            on fa.Id = ftd.AccountId and fa.ParentAccountId = 1
--        inner join AnalyticsSourceDate asd on ft.TransactionDateTime = asd.Date
        
--        Group By DatePart(Year,ft.TransactionDateTime),asd.FiscalWeek
       
--        ) as src )

--Insert into #tempdata
--SELECT Year,Week,WeekAmount
--from data_test
-- Order By Week
 
Select * from #tempdata order by Year,Week

Select 
        DatePart(Year,ft.TransactionDateTime) as Year
        ,DateName(Month,ft.TransactionDateTime) as [Month]
        ,ftd.Amount


        From FinancialTransaction ft
        left Join FinancialTransactionDetail ftd
            on ftd.TransactionId = ft.Id
        left Join FinancialAccount fa
            on fa.Id = ftd.AccountId


        where 
            fa.ParentAccountId = 1
            and fa.IsTaxDeductible = 1
            and TransactionDateTime > '01/01/{{'Now' | Date:'yyyy' | Minus:5}}'
            and ftd.Amount >= 100000
            order by DatePart(Year,ft.TransactionDateTime), DateName(Month,ft.TransactionDateTime)


drop table #tempdata