import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('merger',Path(__file__).with_name('merge_district.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class MergeTests(unittest.TestCase):
 def test_replacements_additions_and_preservation(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'site';src=Path(d)/'source';(root/'data').mkdir(parents=True);src.mkdir()
   games=[{'id':'basket-bros','kind':'game','title':'Basket Bros','url':'old','categories':['Sports'],'image':'old.png'}, {'id':'adventure-capatalist','kind':'game','title':'Adventure Capatalist','url':'old2','categories':['Idle']}, {'id':'unique','kind':'game','title':'Unmatched Game','url':'unchanged','categories':['Arcade'],'metadata':{'exact':True}}, {'id':'neon-2048','kind':'game','title':'Neon 2048','url':'builtin:2048','integrated':True,'categories':['Puzzle']}]
   cat={'games':copy.deepcopy(games),'movies':[{'id':'movie','title':'Movie'}],'cloud':[{'id':'cloud'}],'tools':[{'id':'tool'}]};m.catalog_write(root/'data/catalog.js',cat)
   upstream=[{'name':'Basketbros','href':'basketbros','categories':['Sports']},{'name':'Adventure Capitalist','href':'adventure-capitalist','categories':['Idle']},{'name':'2048','href':'2048','categories':['Puzzle']},{'name':'Brand New','href':'new-game','categories':['Action']},{'name':'Missing Folder','href':'missing','categories':['Puzzle']},{'name':'Unsafe','href':'../secret'}]
   (src/'games.json').write_text(json.dumps(upstream))
   for name in ['basketbros','adventure-capitalist','2048','new-game']:
    f=src/'games'/name/'index.html';f.parent.mkdir(parents=True);f.write_text('<!doctype html><title>'+name+'</title><canvas></canvas>')
   (src/'games/basketbros/payload.data').write_bytes(b'unchanged-native-bytes')
   report=m.merge(root,src,budget_mb=10,commit='fixture-sha');result=m.catalog_read(root/'data/catalog.js');byid={g['id']:g for g in result['games']}
   self.assertEqual(len(report['replaced']),2);self.assertEqual(len(report['added']),2);self.assertEqual(len(report['skipped']),2)
   self.assertEqual(byid['unique'],games[2]);self.assertEqual(byid['neon-2048'],games[3]);self.assertEqual(result['movies'],cat['movies']);self.assertEqual(result['cloud'],cat['cloud']);self.assertEqual(result['tools'],cat['tools']);self.assertEqual((root/'district203/games/basketbros/payload.data').read_bytes(),b'unchanged-native-bytes');self.assertTrue(byid['basket-bros']['nativeAvailable']);self.assertEqual(byid['basket-bros']['id'],'basket-bros');self.assertEqual(byid['basket-bros']['url'],'https://district203.github.io/games/basketbros/')
 def test_no_fuzzy_sequel_matching(self):
  self.assertNotEqual(m.norm('FNAF'),m.norm('FNAF 2'));self.assertNotEqual(m.norm('Geometry Dash'),m.norm('Geometry Dash (Scratch)'))
 def test_unsafe_paths(self):
  for v in ['../x','games/../../secret','a\\b','%2e%2e/x']:
   with self.assertRaises(ValueError):m.safe_path(v)
if __name__=='__main__':unittest.main()
