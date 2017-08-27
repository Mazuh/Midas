# Midas
## The Data Scraper King

Scrapping data from our federal colleges, [UFRN](http://ufrn.br/) and [IFRN](http://portal.ifrn.edu.br/), analysing expenses and producing some cool information for research.

> Download datasets already scraped (on **Kaggle**): https://www.kaggle.com/mazuh69/midas-project

Our Constitution, our Law and our People demand [easy access](http://portal.ifrn.edu.br/acessoainformacao/sobre-a-lei-de-acesso-a-informacao-1/apresentacao-da-lei-de-acesso-lai/at_download/file) to this kind of information in an easier way to understand.

The initial idea is for me to learn and practice data science with Python and R. My **current objective** is to compute statistics for government employees salary. Further, more public expenses will be available for analysis.

## Installing

### Scraper

Did it on my Ubuntu 17 with ```python3``` (3.5), ```pip``` and ```virtualenv``` (from ```pip3```) installed.

After cloning the repository, I changed directory to it and ran:

```
virtualenv .
pip install -r ./requirements.txt
```

Read at the end of ```midas_scraper.py``` file which functions are being called. For a first installation,
there must be all of them not-commented. To run it:

```
./midas_scraper.py
```

That's it. Since there's no relase version yet, be careful with what you're doing and try to understand the code first.

## References

### For development

Inspired by:
- professor [Masanori](https://github.com/fmasanori) and [its students project](https://gist.github.com/fmasanori/6ae7d880da86b61b5f2736da0f341376) that is a data scraper for [USP](http://www5.usp.br/) salaries;
- an [NPI/UFC](https://github.com/npi-ufc-qxd) project named [Dados Abertos](https://github.com/npi-ufc-qxd/dados-abertos) producing [general statistics about federal data](https://crislanio.wordpress.com/2017/06/02/analise-dos-dados-abertos-do-governo-federal/); and
- a [Data Science Brigade](https://github.com/datasciencebr) project called [Serenata de Amor](https://github.com/datasciencebr/serenata-de-amor) for monitoring congressmen expenses using public money (may be similar to my future goal).

A related song:
- "[Ambrosia](https://play.google.com/music/preview/T3glibqusns5cmhzcr6crcnwz34)" by Alesana.

Data sources for this prototype:
- http://www.sistemas.ufrn.br/acessoainformacao/
- http://portal.ifrn.edu.br/acessoainformacao/

### For learning

I'm already comfortable with Python basics and Object Oriented Programming. So there's my reading list:
- [Web Scraping with Python](http://shop.oreilly.com/product/0636920034391.do) by Ryan Mitchell;
- [What you need to know about R](https://www.packtpub.com/packt/free-ebook/what-you-need-know-about-r) by Dipanjan Sarkar & Raghav Bali;
- [Data Analysis with R](https://www.packtpub.com/big-data-and-business-intelligence/data-analysis-r) by Tony Fischetti.

After reading it all, I'll think about more features.

## More

### Mithology

[King Midas](https://en.wikipedia.org/wiki/Midas) was a greek who had the gift (and curse) of transform into gold everything he touches, even his own food and family.

~~So be careful and don't be greedy with the public money, you're being watched.~~

### Legal support

Here in Brazil, since 2011 the law [12.527/11](http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm) specifies the constitutional right of every citizen to know better the public expenses. Therefore, this project is entirely legal.

### License

This project is under [MIT License](./LICENSE).
