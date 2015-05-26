<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node CREATED="1348771118555" ID="ID_1430687192" MODIFIED="1348772486767" TEXT="Hermes">
<node CREATED="1348771166372" ID="ID_56178780" MODIFIED="1353354298970" POSITION="right" TEXT="Hermes API">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Low level and service APIs (this is where the meat of the code is)
    </p>
  </body>
</html></richcontent>
<node CREATED="1348771632892" ID="ID_1232562853" MODIFIED="1357231006997" TEXT="lowLevelApi(engines)">
<node CREATED="1348771458457" ID="ID_772378509" MODIFIED="1348773031385" TEXT="ImportMaps">
<node CREATED="1348771493998" ID="ID_808449820" MODIFIED="1357231011538" TEXT="HermesLegend">
<node CREATED="1348771194769" ID="ID_1582580594" MODIFIED="1349363665638" TEXT="getScopedLegends"/>
<node CREATED="1348771537710" ID="ID_1295927324" MODIFIED="1357231049014" TEXT="saveLegend">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Add an update function for saveLegend has a flag for current (I.E. this template is disabled until it is updated)
    </p>
  </body>
</html>
</richcontent>
</node>
<node CREATED="1348771546463" ID="ID_41042298" MODIFIED="1349210678510" TEXT="deleteLegend"/>
<node CREATED="1348771551472" ID="ID_680210944" MODIFIED="1349210683998" TEXT="getLegend"/>
</node>
<node CREATED="1348771501281" ID="ID_350866390" MODIFIED="1349722759782" TEXT="HermesMap">
<node CREATED="1348771177326" ID="ID_827210259" MODIFIED="1349210537841" TEXT="getMap"/>
<node CREATED="1348771582047" ID="ID_540287802" MODIFIED="1357231214142" TEXT="getScopedMaps"/>
<node CREATED="1348775366786" ID="ID_1585565825" MODIFIED="1349210115056" TEXT="saveMap"/>
<node CREATED="1348775373074" ID="ID_1675133875" MODIFIED="1349722758335" TEXT="deleteMap">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      You must delete map legends before you can delete a map. This will also delete any datastore items connected to this map.
    </p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1348771506895" ID="ID_1550271587" MODIFIED="1357231509966" TEXT="HermesSystems">
<node CREATED="1357231376720" ID="ID_690314930" MODIFIED="1357231384504" TEXT="addDefaultSystems"/>
<node CREATED="1349892749252" ID="ID_1498896762" MODIFIED="1357231346682" TEXT="addNewSystem">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      This is not for updating. this is only for adding a new source that was not added in the addDefaultSources function
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1348775424643" ID="ID_1064511546" MODIFIED="1357231422120" TEXT="deleteSystem">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      You must de-activate any maps before you can delete a source. Note: soft delete
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1348771602912" ID="ID_353608257" MODIFIED="1357231452602" TEXT="getSystems"/>
<node CREATED="1357231460074" ID="ID_781486204" MODIFIED="1357231506485" TEXT="listSystemItems">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      They must have Dynamic Map Helper enabled to use this feature. This also requires a function in the plugin.
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1348775386624" ID="ID_843379296" MODIFIED="1357231523517" TEXT="saveSystem"/>
<node CREATED="1348863561178" ID="ID_1615317644" MODIFIED="1357231567931" TEXT="saveSystemSettings"/>
</node>
</node>
<node CREATED="1348771238251" ID="ID_151212364" MODIFIED="1348773032780" TEXT="DataStore">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      This is the datastore!
    </p>
  </body>
</html></richcontent>
<node CREATED="1348771699586" ID="ID_1011284039" MODIFIED="1348772228800" TEXT="DataStore">
<node CREATED="1348771398717" ID="ID_1510814242" MODIFIED="1348771403561" TEXT="addCurriculogChild"/>
<node CREATED="1349813882116" ID="ID_643859070" MODIFIED="1349813938393" TEXT="addFileData">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Used by acalog to process a file into hermes
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1348771367822" ID="ID_160241449" MODIFIED="1348771373787" TEXT="addItem"/>
<node CREATED="1348771386667" ID="ID_1147584284" MODIFIED="1348771391098" TEXT="addProposal"/>
<node CREATED="1348771393915" ID="ID_857582275" MODIFIED="1348771396620" TEXT="addSections"/>
<node CREATED="1348771405053" ID="ID_1966146385" MODIFIED="1348771408217" TEXT="addFields"/>
<node CREATED="1348771418413" ID="ID_1231903748" MODIFIED="1348771424283" TEXT="checkProposals"/>
<node CREATED="1348771379633" ID="ID_87984007" MODIFIED="1348771384171" TEXT="getItem"/>
<node CREATED="1348771426286" ID="ID_417977764" MODIFIED="1348771430441" TEXT="fileDump"/>
<node CREATED="1348771433244" ID="ID_1107422606" MODIFIED="1348771439802" TEXT="searchDatastore"/>
<node CREATED="1349980060703" ID="ID_1030376292" MODIFIED="1349980062715" TEXT="getDatastoreFields"/>
</node>
<node CREATED="1348771725602" ID="ID_1939503167" MODIFIED="1348771730162" TEXT="StoreAttributes">
<node CREATED="1348771743187" ID="ID_790076327" MODIFIED="1348771748769" TEXT="addAttributes"/>
<node CREATED="1348771750787" ID="ID_1919287999" MODIFIED="1348771757621" TEXT="getAttributes"/>
<node CREATED="1348771759267" ID="ID_457921711" MODIFIED="1348771764481" TEXT="getAPName"/>
<node CREATED="1348771766099" ID="ID_1536675580" MODIFIED="1348771771042" TEXT="getColumnNames"/>
<node CREATED="1348771772562" ID="ID_418357410" MODIFIED="1348771781647" TEXT="getSystemId"/>
</node>
<node CREATED="1348772199466" ID="ID_1786380449" MODIFIED="1349814404859" TEXT="DataStoreImported">
<node CREATED="1348775466866" ID="ID_805210181" MODIFIED="1349814403352" TEXT="markImported">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Will mark that the datastore item was imported into internal source and the internal id
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1349814373287" ID="ID_1205018638" MODIFIED="1349814376238" TEXT="isImported"/>
</node>
</node>
<node CREATED="1348773038456" ID="ID_1984989071" MODIFIED="1348773130841" TEXT="Cron">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Class for running Events on a schedule.
    </p>
  </body>
</html></richcontent>
<node CREATED="1348773210124" ID="ID_924922149" MODIFIED="1348775552442" TEXT="Cron">
<node CREATED="1348773213388" ID="ID_464075142" MODIFIED="1348773214618" TEXT="run"/>
<node CREATED="1348775553972" ID="ID_970277284" MODIFIED="1348775558454" TEXT="addEvent(todo)"/>
</node>
</node>
<node CREATED="1348773047017" ID="ID_729768046" MODIFIED="1348773238669" TEXT="Event">
<node CREATED="1348773224845" ID="ID_1084703587" MODIFIED="1348773226956" TEXT="Event">
<node CREATED="1348773257453" ID="ID_1048067587" MODIFIED="1348773260717" TEXT="_set_months"/>
<node CREATED="1348773266045" ID="ID_658679924" MODIFIED="1348773292522" TEXT="_set_mins"/>
<node CREATED="1348773294221" ID="ID_1824675806" MODIFIED="1348773298330" TEXT="_set_hours"/>
<node CREATED="1348773308992" ID="ID_1309493281" MODIFIED="1348773313933" TEXT="_set_days"/>
<node CREATED="1348773316110" ID="ID_203817027" MODIFIED="1348773320559" TEXT="_set_client"/>
<node CREATED="1348773322223" ID="ID_296815805" MODIFIED="1348773325258" TEXT="matchtime"/>
<node CREATED="1348773326687" ID="ID_578521425" MODIFIED="1348773329071" TEXT="check"/>
</node>
<node CREATED="1348773228555" ID="ID_982806757" MODIFIED="1348773232141" TEXT="convert_to_set"/>
<node CREATED="1348773240348" ID="ID_1052373404" MODIFIED="1348773244011" TEXT="all_match()"/>
<node CREATED="1348773247292" ID="ID_262535401" MODIFIED="1348773251257" TEXT="AllMatch"/>
</node>
</node>
<node CREATED="1348772626615" ID="ID_507940406" MODIFIED="1353353842000" TEXT="ServicesApi(services)">
<node CREATED="1348862332108" ID="ID_1928342722" MODIFIED="1348862334330" TEXT="Services">
<node CREATED="1348866258417" ID="ID_189928634" MODIFIED="1348866261566" TEXT="Maps"/>
<node CREATED="1348866262930" ID="ID_1363683674" MODIFIED="1348866264959" TEXT="Cron"/>
<node CREATED="1348866266129" ID="ID_1996486735" MODIFIED="1348866269354" TEXT="DataStore"/>
</node>
<node CREATED="1348862353242" ID="ID_124609247" MODIFIED="1348862358857" TEXT="webServices"/>
</node>
<node CREATED="1353353815882" ID="ID_298168362" MODIFIED="1353353837863" TEXT="hermes processor">
<node CREATED="1353353861335" ID="ID_506952849" MODIFIED="1353353870891" TEXT="testManager"/>
<node CREATED="1353353877100" ID="ID_427045873" MODIFIED="1353353881309" TEXT="Cron"/>
</node>
</node>
<node CREATED="1348772488335" FOLDED="true" ID="ID_126777672" MODIFIED="1353353812333" POSITION="right" TEXT="Libraries">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Helper libraries and functions for hermes
    </p>
  </body>
</html></richcontent>
<node CREATED="1348772511488" ID="ID_1914437556" MODIFIED="1348772519710" TEXT="findAcalogMatch"/>
<node CREATED="1348772521504" ID="ID_32852112" MODIFIED="1348772528110" TEXT="getSampleData"/>
</node>
<node CREATED="1348772500815" FOLDED="true" ID="ID_1091334697" MODIFIED="1353353939968" POSITION="right" TEXT="Plugins">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Plugins are for the various entry points for data in and out of plugins.
    </p>
  </body>
</html></richcontent>
<node CREATED="1348772539680" ID="ID_791870933" MODIFIED="1348772546108" TEXT="acalog"/>
<node CREATED="1348772974376" ID="ID_846351486" MODIFIED="1348772976566" TEXT="banner"/>
<node CREATED="1348772978152" ID="ID_1787880099" MODIFIED="1348772981398" TEXT="curriculog"/>
<node CREATED="1348772986633" ID="ID_1451370084" MODIFIED="1348773027767" TEXT="bannerlog">
<richcontent TYPE="NOTE"><html>
  <head>
    
  </head>
  <body>
    <p>
      Plugin for using another acalog instance to simulate banner changes and imports into another acalog instance.
    </p>
  </body>
</html></richcontent>
</node>
</node>
</node>
</map>
