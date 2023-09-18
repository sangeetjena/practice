# Learning:  dense rank, group by , filter
# -- Question: find the largest country (in terms of population) in each continent using the table below.
# -- Show the continent, the country name and the population in descending order (the largest country comes first).
# -- (feel free to use your favorite language to solve the problem)
# +---------------+--------------------------+------------+
# | continent     | country                  | population |
# +---------------+--------------------------+------------+
# | North America | United States of America | 324118787  |
# | North America | Canada                   | 36286378   |
# | North America | Mexico                   | 128632004  |
# | Asia          | China                    | 1382323332 |
# | Asia          | India                    | 1326801576 |
# | Asia          | Vietnam                  | 94444200   |

import pandas as pd

contries_df = pd.DataFrame({"continent": ["North America",
                                          "North America",
                                          "North America",
                                          "Asia",
                                          "Asia",
                                          "Asia"],
                            "country": ["Usa",
                                        "Canada",
                                        "Mexico",
                                        "China",
                                        "India",
                                        "Vietnam"],
                            "population": [324118787,
                                           36286378,
                                           128632004,
                                           1382323332,
                                           1326801576,
                                           94444200]})

contries_df["rnk"] = contries_df.groupby("continent")["population"].rank(method="dense", ascending=False)


print(contries_df[contries_df["rnk"] == 1])