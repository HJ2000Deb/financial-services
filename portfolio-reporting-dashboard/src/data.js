/* ==========================================================================
   Sample portfolio data.

   ILLUSTRATIVE ONLY. Every company, figure, ownership stake, valuation and
   submission date below is invented to demonstrate the interface. None of it
   is Debrett's portfolio data and none of it should be quoted, exported or
   shown to a third party as though it were.

   Replace this file with a feed from the system of record before use. The
   shape below is the contract the rest of the application reads:

     periods   string[]                       oldest → newest, quarterly
     companies [{ id, name, sector, stage, hq, firstInvestment, ownership,
                  invested, carryingValue, boardSeat, reporting, commentary,
                  series: { revenue, grossProfit, ebitda, cash, headcount,
                            customers } }]

   All monetary values are £ thousands.
   ========================================================================== */

const DATA = {
  meta: {
    isSample: true,
    asOf: '2026-06-30',
    currentPeriod: '2026 Q2',
    dueDate: '2026-07-31',
    currency: 'GBP',
    unit: 'thousands',
  },

  periods: [
    '2024 Q3', '2024 Q4', '2025 Q1', '2025 Q2',
    '2025 Q3', '2025 Q4', '2026 Q1', '2026 Q2',
  ],

  companies: [
    {
      id: 'marlowe',
      name: 'Marlowe Analytics',
      sector: 'Software & data',
      stage: 'Series B',
      hq: 'London',
      firstInvestment: '2023-05-11',
      ownership: 18.4,
      invested: 6500,
      carryingValue: 11800,
      boardSeat: 'Observer',
      reporting: { status: 'received', submitted: '2026-07-24' },
      commentary:
        'Net revenue retention held above 115% for a fourth consecutive quarter. ' +
        'The enterprise tier now accounts for 41% of bookings. Hiring is being held ' +
        'flat through H2 to reach breakeven on the current cash balance.',
      series: {
        revenue:     [1820, 2050, 2280, 2510, 2790, 3080, 3410, 3720],
        grossProfit: [1420, 1610, 1800, 1985, 2215, 2450, 2730, 2995],
        ebitda:      [-640, -580, -520, -430, -310, -180,  -40,  120],
        cash:        [8900, 8200, 7600, 7050, 6700, 6480, 6350, 6380],
        headcount:   [  84,   89,   95,  101,  108,  114,  119,  123],
        customers:   [ 142,  158,  171,  186,  203,  219,  238,  254],
      },
    },
    {
      id: 'thistlewood',
      name: 'Thistlewood Care',
      sector: 'Healthcare services',
      stage: 'Growth equity',
      hq: 'Leeds',
      firstInvestment: '2022-09-30',
      ownership: 32.0,
      invested: 9200,
      carryingValue: 14600,
      boardSeat: 'Non-executive director',
      reporting: { status: 'received', submitted: '2026-07-18' },
      commentary:
        'Two new local authority frameworks went live in the quarter, taking ' +
        'contracted sites to 47. Agency staff costs fell to 6.1% of payroll, the ' +
        'lowest since acquisition.',
      series: {
        revenue:     [4260, 4380, 4510, 4690, 4820, 5010, 5180, 5340],
        grossProfit: [1490, 1550, 1600, 1680, 1735, 1800, 1865, 1925],
        ebitda:      [ 380,  405,  430,  470,  495,  530,  560,  585],
        cash:        [2100, 2250, 2380, 2560, 2690, 2880, 3050, 3210],
        headcount:   [ 412,  421,  430,  442,  451,  463,  472,  480],
        customers:   [  38,   39,   40,   42,   43,   45,   46,   47],
      },
    },
    {
      id: 'ardenne',
      name: 'Ardenne Foods',
      sector: 'Food & beverage',
      stage: 'Buyout',
      hq: 'Bristol',
      firstInvestment: '2021-11-15',
      ownership: 41.5,
      invested: 11500,
      carryingValue: 9800,
      boardSeat: 'Chair',
      reporting: { status: 'late', submitted: '2026-08-11' },
      commentary:
        'Volumes fell 4.8% against a soft grocery backdrop and the loss of one ' +
        'own-label listing. Working capital absorbed £0.3m in the quarter. The board ' +
        'has asked for a revised 13-week cash forecast and a covenant headroom paper.',
      series: {
        revenue:     [6100, 6450, 5980, 6120, 6040, 6210, 5890, 5760],
        grossProfit: [1830, 1900, 1730, 1780, 1720, 1770, 1620, 1560],
        ebitda:      [ 310,  345,  210,  240,  190,  215,   90,   20],
        cash:        [1850, 1720, 1480, 1390, 1210, 1080,  860,  560],
        headcount:   [ 268,  271,  265,  262,  258,  256,  249,  244],
        customers:   [  21,   22,   21,   22,   22,   23,   22,   21],
      },
    },
    {
      id: 'kelso',
      name: 'Kelso Diagnostics',
      sector: 'Medical technology',
      stage: 'Series A',
      hq: 'Cambridge',
      firstInvestment: '2023-02-08',
      ownership: 14.2,
      invested: 5000,
      carryingValue: 7400,
      boardSeat: 'Observer',
      reporting: { status: 'received', submitted: '2026-07-28' },
      commentary:
        'Regulatory submission for the second assay was filed in May. Commercial ' +
        'traction is ahead of plan at 31 installed sites. A Series B process is ' +
        'expected to open in Q1 2027 on the current burn profile.',
      series: {
        revenue:     [  320,   380,   410,   520,   610,   740,   880,  1030],
        grossProfit: [  150,   182,   201,   260,   311,   385,   466,   556],
        ebitda:      [-1250, -1310, -1290, -1240, -1180, -1120, -1040,  -960],
        cash:        [12400, 11100,  9800,  8560,  7380,  6260,  5220,  4260],
        headcount:   [   62,    66,    68,    71,    74,    76,    78,    80],
        customers:   [    8,     9,    11,    14,    17,    21,    26,    31],
      },
    },
    {
      id: 'pennington',
      name: 'Pennington Logistics',
      sector: 'Logistics & supply chain',
      stage: 'Growth equity',
      hq: 'Manchester',
      firstInvestment: '2022-06-20',
      ownership: 26.8,
      invested: 7800,
      carryingValue: 12300,
      boardSeat: 'Non-executive director',
      reporting: { status: 'received', submitted: '2026-07-22' },
      commentary:
        'Depot utilisation reached 88% and the Midlands hub moved into profit ' +
        'a quarter early. Fuel hedging covers 70% of forecast H2 consumption.',
      series: {
        revenue:     [2940, 3120, 3080, 3350, 3520, 3760, 3910, 4180],
        grossProfit: [1030, 1105, 1085, 1195, 1265, 1360, 1425, 1535],
        ebitda:      [ 120,  165,  140,  220,  265,  330,  370,  445],
        cash:        [3400, 3520, 3480, 3650, 3810, 4020, 4180, 4420],
        headcount:   [ 156,  161,  159,  166,  172,  178,  182,  189],
        customers:   [  74,   78,   77,   83,   88,   94,   98,  104],
      },
    },
    {
      id: 'wrayford',
      name: 'Wrayford Energy',
      sector: 'Energy transition',
      stage: 'Series B',
      hq: 'Glasgow',
      firstInvestment: '2023-09-04',
      ownership: 22.5,
      invested: 6200,
      carryingValue: 9900,
      boardSeat: 'Observer',
      reporting: { status: 'outstanding', submitted: null },
      commentary:
        'No return received for the quarter. The finance director left in June and ' +
        'a replacement starts in September; management has been asked to confirm a ' +
        'submission date in writing.',
      series: {
        revenue:     [1980, 2240, 2410, 2680, 2950, 3210, 3480, 3690],
        grossProfit: [ 594,  683,  747,  844,  944, 1027, 1131, 1218],
        ebitda:      [-180, -120,  -60,   40,  130,  210,  300,  380],
        cash:        [5600, 5380, 5240, 5310, 5480, 5710, 6020, 6350],
        headcount:   [  98,  104,  109,  116,  123,  129,  136,  142],
        customers:   [  46,   51,   55,   61,   67,   73,   80,   86],
      },
    },
    {
      id: 'colvine',
      name: 'Colvine Learning',
      sector: 'Education technology',
      stage: 'Series A',
      hq: 'Edinburgh',
      firstInvestment: '2022-03-14',
      ownership: 19.7,
      invested: 4400,
      carryingValue: 3600,
      boardSeat: 'Observer',
      reporting: { status: 'late', submitted: '2026-08-06' },
      commentary:
        'Revenue has been flat for six quarters and the institutional renewal rate ' +
        'slipped to 81%. The carrying value was written down at the March review. ' +
        'A strategic options paper is due to the board in October.',
      series: {
        revenue:     [1450, 1520, 1480, 1510, 1460, 1490, 1440, 1410],
        grossProfit: [1030, 1085, 1050, 1075, 1035, 1058, 1015,  990],
        ebitda:      [-320, -280, -300, -270, -290, -260, -280, -300],
        cash:        [4100, 3820, 3520, 3260, 2970, 2710, 2430, 2130],
        headcount:   [  71,   72,   70,   69,   68,   66,   65,   63],
        customers:   [ 310,  324,  318,  327,  321,  330,  322,  314],
      },
    },
    {
      id: 'halsey',
      name: 'Halsey & Croft',
      sector: 'Insurance services',
      stage: 'Buyout',
      hq: 'London',
      firstInvestment: '2021-07-01',
      ownership: 35.4,
      invested: 10200,
      carryingValue: 18700,
      boardSeat: 'Chair',
      reporting: { status: 'received', submitted: '2026-07-15' },
      commentary:
        'Commission income grew 14.6% year on year with retention at 94%. The ' +
        'second bolt-on completed in April and is integrating to plan.',
      series: {
        revenue:     [3620, 3780, 3910, 4080, 4260, 4470, 4650, 4880],
        grossProfit: [2534, 2646, 2737, 2856, 2982, 3129, 3255, 3416],
        ebitda:      [ 690,  745,  790,  850,  910,  985, 1045, 1120],
        cash:        [2800, 2980, 3160, 3390, 3620, 3900, 4160, 4470],
        headcount:   [ 118,  121,  124,  128,  132,  137,  141,  146],
        customers:   [1240, 1290, 1335, 1392, 1448, 1516, 1578, 1652],
      },
    },
  ],

  /* Which return landed, for which quarter — drives the collection tracker.
     Keyed by company id; one entry per period, oldest → newest. */
  submissions: {
    marlowe:    ['received', 'received', 'received', 'received', 'received', 'received', 'received', 'received'],
    thistlewood:['received', 'received', 'received', 'received', 'received', 'received', 'received', 'received'],
    ardenne:    ['received', 'late', 'received', 'late', 'received', 'late', 'late', 'late'],
    kelso:      ['received', 'received', 'received', 'received', 'received', 'received', 'received', 'received'],
    pennington: ['received', 'received', 'late', 'received', 'received', 'received', 'received', 'received'],
    wrayford:   ['received', 'received', 'received', 'late', 'received', 'received', 'late', 'outstanding'],
    colvine:    ['late', 'received', 'late', 'received', 'late', 'late', 'received', 'late'],
    halsey:     ['received', 'received', 'received', 'received', 'received', 'received', 'received', 'received'],
  },

  /* The metric set a portfolio company is asked to return each quarter. */
  requestedMetrics: [
    { key: 'revenue',     label: 'Revenue',            unit: '£000', help: 'Recognised revenue for the quarter, net of discounts and credits.' },
    { key: 'grossProfit', label: 'Gross profit',       unit: '£000', help: 'Revenue less direct cost of sale. Exclude central overhead.' },
    { key: 'ebitda',      label: 'EBITDA',             unit: '£000', help: 'Before exceptional items. Show a loss as a negative figure.' },
    { key: 'cash',        label: 'Cash at quarter end', unit: '£000', help: 'Cash and equivalents on the last day of the quarter.' },
    { key: 'headcount',   label: 'Headcount',          unit: 'FTE',  help: 'Full-time equivalents on the payroll at quarter end.' },
    { key: 'customers',   label: 'Customers',          unit: 'count', help: 'Active paying customers, sites or contracts at quarter end.' },
  ],
};
