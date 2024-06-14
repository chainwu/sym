## 繁體中文 -> 簡體中文
```
$ python3 -m opencc -c t2s -i grape.txt -o crape.txt
```

## sym.py
把不常見的中文字變成常見的同音字，換掉的字後面有星號。舉例
```
cat grape.txt
葡萄美酒夜光杯，欲饮琵琶马上催

$ python3 sym.py crape.txt > srape.txt
$ cat srape.txt
脯* 桃* 美 酒 夜 光 杯 欲 饮 疲* 爬* 马 上 催
```
## 去掉星號
```
sed -i 's/\*//g' srape.txt
```

## text_recovery.py
把處理完的 textgrid file 中間換掉的字恢復
```
                        <textgrid file> <original text> <replaced textgrid file>
python3 text_recovery.py grape.textgrid grape.txt grape-phoneme.textgrid
```

## sampa2ipa.py
把 SAMPA 轉成 IPA
```
python3 sampa2ipa.py grape-phoneme.textgrid grape-ipa.textgrid
```
