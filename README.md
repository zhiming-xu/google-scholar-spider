## Disclaimer
The data collected by this program comes *wholely* from public domain, i.e., institutions' official websites, Google search results, and
Google Scholar. Neither does it reflect my personal opinion nor serve as advise of any kind. The way how you interpret it
depends solely on yourself: your idea, belief, personal experiences and/or any other things that could result in a particular
attitude towards it. I modify nothing but make the data more readable and concise. There are a few issues which can produce potential
mistakes. They are discussed in the following [Known Issues](#Known-Issues) and also noted in codes as `FIXME`. If you are suspicious of any result, please consult with them and codes first. This program *might* cause your IP address banned by Google and/or other website owners, whether temporarily or permanently. By running it, you must be aware that it is all at your own risk. I am *by all means* not responsible for any direct and indirect consequences following such ban.

## Known Issues
### Name extracting
- By now, I simply assume that the first character in a Chinese name stands for surname, and the characters left stand for given name.
Apparently, for compound surnames, this will not work. I am considering adding rigid rules to handle this. If you have a better idea, please kindly tell me.
- This situation might be rare, but chances are that some faculty members affiliated with the same institutions have the same name, or the same pinyin representation of their names. Current code will treat them as the same person.
### Google search
- The query I use is of form `[given_name] [surname] [affiliated_institution]`, and I only look for the first hyperlink to a Google scholar site in the first page of searching result. So if the link does not appear in the first page, I will assume that this faculty member does not have such a website and ignore his/her connections. I believe with such an exact query, Google will give me the link as long as it does exist.
### Institution list processing
- This is a truly annoying part. Google Scholar does not have a standard way of demonstrating a researcher's affiliated institution. The parsed result might be just the institution's name, or mix with stopwords, the researcher's title, position and/or other characters. This can result in duplicated representations of the same institution, wrong institution name or other weird behavior. I will try to use more rules and parse tools to minimize the negative effect.