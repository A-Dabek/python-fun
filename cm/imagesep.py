import cm.CardSplitter
import cm.CardReader as CardReader
import cm.CardCollector
#CardSplitter.prepareRawCards("shots/")
CardReader.processRawCards("raw/")
#cards_list = CardCollector.getCardsBy("processed/", key_tag='war')
#print(cards_list)



