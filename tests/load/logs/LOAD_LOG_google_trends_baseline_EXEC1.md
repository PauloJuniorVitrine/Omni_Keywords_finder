[2025-05-31 23:25:31,333] PC011/INFO/locust.main: Starting Locust 2.36.2 (locust-cloud 1.20.7)
[2025-05-31 23:25:32,104] PC011/INFO/locust.main: Run time limit set to 60 seconds
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         0     0(0.00%) |      0       0       0      0 |    0.00        0.00

[2025-05-31 23:25:32,129] PC011/INFO/locust.runners: Ramping to 10 users at a rate of 1.00 per second
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         0     0(0.00%) |      0       0       0      0 |    0.00        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         2     0(0.00%) |   2557    2051    3064   2100 |    0.00        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         3     0(0.00%) |   2383    2034    3064   2100 |    0.00        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.17        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.17        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.17        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                         7     0(0.00%) |   2479    2034    3064   2100 |    0.50        0.00

[2025-05-31 23:25:41,204] PC011/INFO/locust.runners: All users spawned: {"GoogleTrendsUser": 10} (10 total users)
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.14        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.14        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.14        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.14        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.14        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        11     0(0.00%) |   2599    2034    3078   3000 |    0.71        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.11        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.11        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.11        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.11        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.11        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.11        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.11        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.11        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        17     0(0.00%) |   2471    2034    3078   2100 |    0.89        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        21     0(0.00%) |   2394    2034    3078   2100 |    1.70        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        26     0(0.00%) |   2445    2034    3086   2100 |    1.80        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.10        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        30     0(0.00%) |   2427    2034    3086   2100 |    2.00        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.10        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        36     0(0.00%) |   2476    2025    3086   2100 |    2.40        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        40     0(0.00%) |   2434    2025    3086   2100 |    2.30        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        45     0(0.00%) |   2415    2025    3086   2100 |    2.20        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.10        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        49     0(0.00%) |   2406    2025    3086   2100 |    2.70        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.10        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.10        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        54     0(0.00%) |   2410    2025    3086   2100 |    2.20        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        60     0(0.00%) |   2395    2025    3086   2100 |    2.30        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        65     0(0.00%) |   2370    2025    3086   2100 |    2.50        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        68     0(0.00%) |   2371    2025    3086   2100 |    2.40        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        75     0(0.00%) |   2382    2025    3089   2100 |    2.10        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.10        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        77     0(0.00%) |   2387    2025    3089   2100 |    2.50        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.10        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.10        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.10        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        84     0(0.00%) |   2383    2025    3089   2100 |    2.50        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.10        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.10        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        87     0(0.00%) |   2383    2025    3089   2100 |    2.20        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.00        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.10        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.10        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        93     0(0.00%) |   2372    2025    3089   2100 |    2.40        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.10        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.10        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.10        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.10        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        96     0(0.00%) |   2372    2025    3089   2100 |    2.60        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.10        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.10        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.10        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       103     0(0.00%) |   2370    2025    3089   2100 |    2.20        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.10        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                  1     0(0.00%) |   2020    2020    2020   2020 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.10        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.00        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.10        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.10        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       106     0(0.00%) |   2370    2020    3089   2100 |    2.40        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.10        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbxza&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayaaay                                            1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxbyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.10        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                  1     0(0.00%) |   2020    2020    2020   2020 |    0.00        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cczccb&simular=resposta_invalida                  1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxxax&simular=timeout                            1     0(0.00%) |   3048    3048    3048   3048 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.10        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.10        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.10        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       111     0(0.00%) |   2364    2020    3089   2100 |    2.00        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbxza&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayaaay                                            1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxbyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxcb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.10        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                  1     0(0.00%) |   2020    2020    2020   2020 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzxaac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzxbxz&simular=erro_autenticacao                  1     0(0.00%) |   2090    2090    2090   2090 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=cccxya&simular=resposta_invalida                  1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cczccb&simular=resposta_invalida                  1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxxax&simular=timeout                            1     0(0.00%) |   3048    3048    3048   3048 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.10        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.10        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.10        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.00        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       115     0(0.00%) |   2363    2020    3089   2100 |    2.10        0.00

Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.00        0.00
GET      /api/externo/google_trends?termo=abcxcx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.00        0.00
GET      /api/externo/google_trends?termo=acbxza&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.10        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayaaay                                            1     0(0.00%) |   2055    2055    2055   2055 |    0.10        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.00        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                  1     0(0.00%) |   2071    2071    2071   2071 |    0.10        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.00        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.00        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.00        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.00        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxbyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxcb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.10        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.00        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.00        0.00
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                  1     0(0.00%) |   2020    2020    2020   2020 |    0.10        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.00        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.00        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.10        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzxaac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=bzxbxz&simular=erro_autenticacao                  1     0(0.00%) |   2090    2090    2090   2090 |    0.10        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.00        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.00        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.00        0.00
GET      /api/externo/google_trends?termo=cccxya&simular=resposta_invalida                  1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.10        0.00
GET      /api/externo/google_trends?termo=cczccb&simular=resposta_invalida                  1     0(0.00%) |   2044    2044    2044   2044 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.10        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.00        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.00        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.00        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.00        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbxxax&simular=timeout                            1     0(0.00%) |   3048    3048    3048   3048 |    0.10        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.00        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.00        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.00        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.10        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.00        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.00        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.00        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.00        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.10        0.00
GET      /api/externo/google_trends?termo=yczbxa                                            1     0(0.00%) |   2052    2052    2052   2052 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.10        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yybxyx&simular=resposta_invalida                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxbca&simular=erro_autenticacao                  1     0(0.00%) |   2039    2039    2039   2039 |    0.00        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.00        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.00        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.10        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.00        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.00        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zczzzz&simular=erro_autenticacao                  1     0(0.00%) |   2057    2057    2057   2057 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.10        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.00        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.00        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.10        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.00        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.00        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.00        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.00        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       120     0(0.00%) |   2358    2020    3089   2100 |    2.20        0.00

[2025-05-31 23:26:30,222] PC011/INFO/locust.main: --run-time limit reached, shutting down
[2025-05-31 23:26:30,386] PC011/INFO/locust.main: Shutting down (exit code 0)
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /api/externo/google_trends?termo=aacxyc                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.02        0.00
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.02        0.00
GET      /api/externo/google_trends?termo=aazccc                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.02        0.00
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                  1     0(0.00%) |   2041    2041    2041   2041 |    0.02        0.00
GET      /api/externo/google_trends?termo=abcxcx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.02        0.00
GET      /api/externo/google_trends?termo=acbxza&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.02        0.00
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                            1     0(0.00%) |   3079    3079    3079   3079 |    0.02        0.00
GET      /api/externo/google_trends?termo=axccxy                                            1     0(0.00%) |   2070    2070    2070   2070 |    0.02        0.00
GET      /api/externo/google_trends?termo=ayaaay                                            1     0(0.00%) |   2055    2055    2055   2055 |    0.02        0.00
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                            1     0(0.00%) |   3070    3070    3070   3070 |    0.02        0.00
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                  1     0(0.00%) |   2122    2122    2122   2122 |    0.02        0.00
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.02        0.00
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.02        0.00
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                  1     0(0.00%) |   2071    2071    2071   2071 |    0.02        0.00
GET      /api/externo/google_trends?termo=azcxac                                            1     0(0.00%) |   2064    2064    2064   2064 |    0.02        0.00
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                            1     0(0.00%) |   3034    3034    3034   3034 |    0.02        0.00
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                            1     0(0.00%) |   3084    3084    3084   3084 |    0.02        0.00
GET      /api/externo/google_trends?termo=azzxxb                                            1     0(0.00%) |   2035    2035    2035   2035 |    0.02        0.00
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                  1     0(0.00%) |   2074    2074    2074   2074 |    0.02        0.00
GET      /api/externo/google_trends?termo=babyxb                                            1     0(0.00%) |   2056    2056    2056   2056 |    0.02        0.00
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                            1     0(0.00%) |   3071    3071    3071   3071 |    0.02        0.00
GET      /api/externo/google_trends?termo=bbxbyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.02        0.00
GET      /api/externo/google_trends?termo=bbxxcb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.02        0.00
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.02        0.00
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                  1     0(0.00%) |   2069    2069    2069   2069 |    0.02        0.00
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                  1     0(0.00%) |   2040    2040    2040   2040 |    0.02        0.00
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                  1     0(0.00%) |   2063    2063    2063   2063 |    0.02        0.00
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                            1     0(0.00%) |   3053    3053    3053   3053 |    0.02        0.00
GET      /api/externo/google_trends?termo=bxxxca                                            1     0(0.00%) |   2025    2025    2025   2025 |    0.02        0.00
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                  1     0(0.00%) |   2020    2020    2020   2020 |    0.02        0.00
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                  1     0(0.00%) |   2066    2066    2066   2066 |    0.02        0.00
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                            1     0(0.00%) |   3042    3042    3042   3042 |    0.02        0.00
GET      /api/externo/google_trends?termo=byyzyy                                            1     0(0.00%) |   2074    2074    2074   2074 |    0.02        0.00
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                            1     0(0.00%) |   3068    3068    3068   3068 |    0.02        0.00
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                            1     0(0.00%) |   3052    3052    3052   3052 |    0.02        0.00
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.02        0.00
GET      /api/externo/google_trends?termo=bzxaac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.02        0.00
GET      /api/externo/google_trends?termo=bzxbxz&simular=erro_autenticacao                  1     0(0.00%) |   2090    2090    2090   2090 |    0.02        0.00
GET      /api/externo/google_trends?termo=bzxyca&simular=timeout                            1     0(0.00%) |   3040    3040    3040   3040 |    0.02        0.00
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                  1     0(0.00%) |   2084    2084    2084   2084 |    0.02        0.00
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.02        0.00
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                  1     0(0.00%) |   2046    2046    2046   2046 |    0.02        0.00
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.02        0.00
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                            1     0(0.00%) |   3045    3045    3045   3045 |    0.02        0.00
GET      /api/externo/google_trends?termo=cbyzbc&simular=erro_autenticacao                  1     0(0.00%) |   2059    2059    2059   2059 |    0.02        0.00
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                  1     0(0.00%) |   2074    2074    2074   2074 |    0.02        0.00
GET      /api/externo/google_trends?termo=cccxya&simular=resposta_invalida                  1     0(0.00%) |   2048    2048    2048   2048 |    0.02        0.00
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.02        0.00
GET      /api/externo/google_trends?termo=cczccb&simular=resposta_invalida                  1     0(0.00%) |   2044    2044    2044   2044 |    0.02        0.00
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                  1     0(0.00%) |   2053    2053    2053   2053 |    0.02        0.00
GET      /api/externo/google_trends?termo=cxccxy                                            1     0(0.00%) |   2054    2054    2054   2054 |    0.02        0.00
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                  1     0(0.00%) |   2071    2071    2071   2071 |    0.02        0.00
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                  1     0(0.00%) |   2059    2059    2059   2059 |    0.02        0.00
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.02        0.00
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                  1     0(0.00%) |   2050    2050    2050   2050 |    0.02        0.00
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                  1     0(0.00%) |   2133    2133    2133   2133 |    0.02        0.00
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                  1     0(0.00%) |   2089    2089    2089   2089 |    0.02        0.00
GET      /api/externo/google_trends?termo=czzcbz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.02        0.00
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                  1     0(0.00%) |   2043    2043    2043   2043 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbxabx                                            1     0(0.00%) |   2034    2034    2034   2034 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbxxax&simular=timeout                            1     0(0.00%) |   3048    3048    3048   3048 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.02        0.00
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                            1     0(0.00%) |   3061    3061    3061   3061 |    0.02        0.00
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                            1     0(0.00%) |   3082    3082    3082   3082 |    0.02        0.00
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                  1     0(0.00%) |   2091    2091    2091   2091 |    0.02        0.00
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                  1     0(0.00%) |   2050    2050    2050   2050 |    0.02        0.00
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                            1     0(0.00%) |   3046    3046    3046   3046 |    0.02        0.00
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.02        0.00
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                  1     0(0.00%) |   2047    2047    2047   2047 |    0.02        0.00
GET      /api/externo/google_trends?termo=xyzxyb                                            1     0(0.00%) |   2047    2047    2047   2047 |    0.02        0.00
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                            1     0(0.00%) |   3086    3086    3086   3086 |    0.02        0.00
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                            1     0(0.00%) |   3065    3065    3065   3065 |    0.02        0.00
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                            1     0(0.00%) |   3037    3037    3037   3037 |    0.02        0.00
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                  1     0(0.00%) |   2049    2049    2049   2049 |    0.02        0.00
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                  1     0(0.00%) |   2096    2096    2096   2096 |    0.02        0.00
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                  1     0(0.00%) |   2067    2067    2067   2067 |    0.02        0.00
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                  1     0(0.00%) |   2051    2051    2051   2051 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                            1     0(0.00%) |   3089    3089    3089   3089 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                  1     0(0.00%) |   2057    2057    2057   2057 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                  1     0(0.00%) |   2051    2051    2051   2051 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                  1     0(0.00%) |   2118    2118    2118   2118 |    0.02        0.00
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                  1     0(0.00%) |   2034    2034    2034   2034 |    0.02        0.00
GET      /api/externo/google_trends?termo=yczbxa                                            1     0(0.00%) |   2052    2052    2052   2052 |    0.02        0.00
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.02        0.00
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                            1     0(0.00%) |   3049    3049    3049   3049 |    0.02        0.00
GET      /api/externo/google_trends?termo=yxyxcz                                            1     0(0.00%) |   2048    2048    2048   2048 |    0.02        0.00
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                            1     0(0.00%) |   3078    3078    3078   3078 |    0.02        0.00
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.02        0.00
GET      /api/externo/google_trends?termo=yybxyx&simular=resposta_invalida                  1     0(0.00%) |   2054    2054    2054   2054 |    0.02        0.00
GET      /api/externo/google_trends?termo=yyxbca&simular=erro_autenticacao                  1     0(0.00%) |   2039    2039    2039   2039 |    0.02        0.00
GET      /api/externo/google_trends?termo=yyxczc                                            1     0(0.00%) |   2045    2045    2045   2045 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                  1     0(0.00%) |   2040    2040    2040   2040 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzxxyz                                            1     0(0.00%) |   2044    2044    2044   2044 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzzaaa                                            1     0(0.00%) |   2043    2043    2043   2043 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                  1     0(0.00%) |   2037    2037    2037   2037 |    0.02        0.00
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                  1     0(0.00%) |   2063    2063    2063   2063 |    0.02        0.00
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                  1     0(0.00%) |   2031    2031    2031   2031 |    0.02        0.00
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                            1     0(0.00%) |   3075    3075    3075   3075 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbaaaz&simular=timeout                            1     0(0.00%) |   3055    3055    3055   3055 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbcaxx                                            1     0(0.00%) |   2049    2049    2049   2049 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                  1     0(0.00%) |   2055    2055    2055   2055 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                  1     0(0.00%) |   2053    2053    2053   2053 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                  1     0(0.00%) |   2042    2042    2042   2042 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                            1     0(0.00%) |   3081    3081    3081   3081 |    0.02        0.00
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                  1     0(0.00%) |   2056    2056    2056   2056 |    0.02        0.00
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                            1     0(0.00%) |   3064    3064    3064   3064 |    0.02        0.00
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                            1     0(0.00%) |   3056    3056    3056   3056 |    0.02        0.00
GET      /api/externo/google_trends?termo=zczzzz&simular=erro_autenticacao                  1     0(0.00%) |   2057    2057    2057   2057 |    0.02        0.00
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                            1     0(0.00%) |   3044    3044    3044   3044 |    0.02        0.00
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                  1     0(0.00%) |   2130    2130    2130   2130 |    0.02        0.00
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                  1     0(0.00%) |   2056    2056    2056   2056 |    0.02        0.00
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                  1     0(0.00%) |   2049    2049    2049   2049 |    0.02        0.00
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                            1     0(0.00%) |   3059    3059    3059   3059 |    0.02        0.00
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                  1     0(0.00%) |   2048    2048    2048   2048 |    0.02        0.00
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                  1     0(0.00%) |   2043    2043    2043   2043 |    0.02        0.00
GET      /api/externo/google_trends?termo=zycczc                                            1     0(0.00%) |   2040    2040    2040   2040 |    0.02        0.00
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                            1     0(0.00%) |   3051    3051    3051   3051 |    0.02        0.00
GET      /api/externo/google_trends?termo=zzxyay                                            1     0(0.00%) |   2075    2075    2075   2075 |    0.02        0.00
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                  1     0(0.00%) |   2054    2054    2054   2054 |    0.02        0.00
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                            1     0(0.00%) |   3080    3080    3080   3080 |    0.02        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                       124     0(0.00%) |   2364    2020    3089   2100 |    2.14        0.00

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /api/externo/google_trends?termo=aacxyc                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=aayczx&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=aazccc                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=aazyyx&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=abcxcx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=acbxza&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=acbzbb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=axccxy                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ayaaay                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=aycacx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=ayxybc&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ayyaza&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=ayzxxy&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=azaabb&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=azcxac                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=azxbzz&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=azybcc&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=azzxxb                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=babcca&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=babyxb                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bbczxy&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=bbxbyz&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=bbxxcb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=bbxxzc&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bbxzaz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bcbybb&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=bczzxc&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bxbcxy&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=bxxxca                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=bxxzca&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=byayzy&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bycbcb&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=byyzyy                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=byzbbb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=byzbyx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=bzcyzb&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bzxaac&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=bzxbxz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=bzxyca&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=bzyxxy&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cacbya&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cbaxac&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=cbcxba&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=cbxxcc&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=cbyzbc&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ccbxcx&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cccxya&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=ccyzxa&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cczccb&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=cxcaby&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cxccxy                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cxxbcy&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cybbby&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cycyzc&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=cyxabx&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cyxyca&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=cyzzax&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=czzcbz                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=xaacxa&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=xbabza&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=xbcxyc&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=xbxabx                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=xbxxax&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=xbyxcz&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=xbzbyx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=xcbcab&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=xcxyza&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=xcybzx&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=xcyczc&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=xxcycz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=xybyza&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=xyzxyb                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=xzaaxx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=yabbcy&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=yayyca&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=yayyyz&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=ybaazy&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ybzccx&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ybzzac&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ycbyza&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=ycbzyc&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=ycxbya&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ycxyaa&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ycxyaz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=ycxycy&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yczbxa                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=yxxayy&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yxyayz&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=yxyxcz                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yyacby&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=yyazza&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=yybxyx&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=yyxbca&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yyxczc                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yzabax&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yzbzbx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=yzxxyz                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yzzaaa                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yzzccy&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=yzzyzy&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zabxzz&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zacycy&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zbaaaz&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zbcaxx                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zbybyb&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zbycaa&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zbycxx&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zbyyxc&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zbzaya&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zcaxcy&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zccccb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zczzzz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zxacac&simular=timeout                              3000   3000   3000   3000   3000   3000   3000   3000   3000   3000   3000      1
GET      /api/externo/google_trends?termo=zxxccy&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zxxxzz&simular=resposta_invalida                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zxxzby&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zxzccb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zybzbc&simular=erro_autenticacao                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zycbaa&simular=resposta_invalida                    2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zycczc                                              2000   2000   2000   2000   2000   2000   2000   2000   2000   2000   2000      1
GET      /api/externo/google_trends?termo=zyzabb&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
GET      /api/externo/google_trends?termo=zzxyay                                              2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zzyczz&simular=erro_autenticacao                    2100   2100   2100   2100   2100   2100   2100   2100   2100   2100   2100      1
GET      /api/externo/google_trends?termo=zzzxxx&simular=timeout                              3100   3100   3100   3100   3100   3100   3100   3100   3100   3100   3100      1
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                           2100   2100   3000   3100   3100   3100   3100   3100   3100   3100   3100    124

