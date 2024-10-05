# wca
World Cube Association CLI
---
CLI that parses https://worldcubeassociation.org and provides formatted data

### Setup:

```commandline
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirement.txt
```

### Usage:
```commandline
usage: wca.py [-h] [--format {short,csv,json}] [--concurrency CONCURRENCY]
              {competitions,competitors,competitor-stats,person} ...

World Cube Association CLI

positional arguments:
  {competitions,competitors,competitor-stats,person}

options:
  -h, --help            show this help message and exit
  --format {short,csv,json}, -f {short,csv,json}
                        format
  --concurrency CONCURRENCY, -c CONCURRENCY
                        remote call concurrency
```

#### List Competitions
```commandline
(venv) % ./wca.py competitions --help
usage: wca.py competitions [-h] [--search SEARCH]

options:
  -h, --help            show this help message and exit
  --search SEARCH, -s SEARCH
                        search keywords

# example

(venv) % ./wca.py competitions --search california
[2024/10/13] Berkeley Fall 2024 (BerkeleyFall2024)
[2024/10/18] UCSD Weeknights I 2024 (UCSDWeeknightsI2024)
[2024/10/19] UCSB Cubing 2024 (UCSBCubing2024)
[2024/10/20] Davis Fall 2024 (DavisFall2024)
[2024/10/21] Berkeley Oct Tricubealon 2024 (BerkeleyOctoberTricubealon2024)
[2024/10/26] Temecula Valley Fall 2024 (TemeculaValleyFall2024)
[2024/11/03] Cool Down Berkeley 2024 (CoolDownBerkeley2024)
[2024/11/09] BASC 66 - Belmont 2024 (BASC66Belmont2024)
[2024/11/18] Berkeley Nov Tricubealon 2024 (BerkeleyNovemberTricubealon2024)
```

#### List Competitors
```commandline
(venv) % ./wca.py competitors --help
usage: wca.py competitors [-h] competition_id

positional arguments:
  competition_id  Competition ID

options:
  -h, --help      show this help message and exit

# example

(venv) % ./wca.py competitors TemeculaValleyFall2024
Aayush Manish Bathija (2019BATH02)
Adam Cayne Emmons
Adlan Darpi (2024DARP01)
Alejandro Gutierrez (2022GUTI09)
Alex Lehman (2015LEHM01)
Alexander Anikin (ÐÐ»ÐµÐºÑÐ°Ð½Ð´Ñ ÐÐ½Ð¸ÐºÐ¸Ð½) (2021ANIK01)
Alexander Segal (2023SEGA03)
Amber Trueblood (2023TRUE03)
Amogh Adluri (2018ADLU01)
Anders Arnsten (2022ARNS01)
Anders Bogan (2011BOGA01)
Angel Claire Borja (2024BORJ01)
Anthony Hernandez (2024HERN10)
Aras Benson Casciato (2024CASC03)
...
```

#### Get Competitor Stats

```commandline
(venv) % ./wca.py competitor-stats --help
usage: wca.py competitor-stats [-h]
                               [--event {333,222,444,555,666,333bf,333oh,clock,minx,pyram,skewb,sq1}]
                               competition_id

positional arguments:
  competition_id        Competition ID

options:
  -h, --help            show this help message and exit
  --event {333,222,444,555,666,333bf,333oh,clock,minx,pyram,skewb,sq1}
                        display average time stats for the given event

# example

(venv) % ./wca.py competitor-stats TemeculaValleyFall2024 --event 333
min: 4.86
max: 102.33
mean: 20.58875968992248
25p: 11.025
median: 15.36
75p: 24.135
95p: 59.02
99p: 95.78699999999999
```

#### Get Person
```commandline
(venv) % ./wca.py competitions --help
usage: wca.py competitions [-h] [--search SEARCH]

options:
  -h, --help            show this help message and exit
  --search SEARCH, -s SEARCH
                        search keywords
(venv) % ./wca.py person --help
usage: wca.py person [-h] person_id

positional arguments:
  person_id   Person ID

options:
  -h, --help  show this help message and exit

# example
  
(venv) % ./wca.py person 2019BATH02
------------------------------------
[Rank 1638] Aayush Manish Bathija (2019BATH02)
------------------------------------
[222]	: 2.92 (Rank 2841)
[333]	: 9.38 (Rank 1638)
[333bf]	: 0.0 (Rank 5094)
[333oh]	: 27.58 (Rank 15766)
[444]	: 44.28 (Rank 3074)
[555]	: 110.67 (Rank 10832)
[666]	: 456.08 (Rank 9681)
[clock]	: 19.16 (Rank 10353)
[minx]	: 0.0 (Rank 20774)
[pyram]	: 7.79 (Rank 12779)
[skewb]	: 15.2 (Rank 24956)
[sq1]	: 25.33 (Rank 4108)
```

### Event definitions
| Event Key | Description       |
|-----------|-------------------|
| 333       | 3x3x3             |
| 222       | 2x2x2             |
| 444       | 4x4x4             |
| 555       | 5x5x5             |
| 666       | 6x6x6             |
| 333bf     | 3x3x3 Blindfolded |
| 333oh     | 3x3x3 One-handed  |
| clock     | Clock             |
| minx      | Megaminx          |
| pyram     | Pyraminx          |
| skewb     | Skewb             |
| sq1       | Square-1          |
