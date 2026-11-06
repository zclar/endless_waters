"""Native Bedrock loot tables: rolls happen on first access and persist normally."""
from sea_life import save
ROLES={
 'crew':[('bread',8,1,4),('string',6,1,5),('paper',5,1,4),('emerald',1,1,2)],
 'supplies':[('iron_ingot',5,1,5),('copper_ingot',6,2,8),('coal',8,2,8),('torch',8,3,12),('leather',5,1,4)],
 'cargo':[('spruce_planks',9,4,20),('iron_nugget',7,3,14),('string',7,2,9),('coal',7,2,9),('gold_ingot',1,1,3)],
 'salvage':[('bone',8,1,8),('rotten_flesh',7,1,5),('iron_nugget',7,1,10),('amethyst_shard',3,1,4),('emerald',1,1,3)],
 'pantry':[('endless:food_kelp_roll',7,1,4),('endless:food_salted_cod',7,1,4),('endless:food_seafood_stew',2,1,2),('bread',7,1,5),('carrot',5,1,5)],
 'armory':[('arrow',12,5,20),('gunpowder',8,2,8),('iron_ingot',5,1,4),('crossbow',1,1,1),('iron_sword',1,1,1)],
 'vault':[('gold_ingot',8,2,7),('emerald',8,2,8),('amethyst_shard',7,2,7),('iron_ingot',6,3,8),('gold_nugget',10,5,18)],
 'captain':[('emerald',6,1,5),('gold_ingot',6,1,4),('book',5,1,4),('compass',2,1,1),('amethyst_shard',5,1,4)],
 'navigation':[('paper',9,3,12),('book',5,1,3),('compass',3,1,1),('spyglass',2,1,1),('clock',1,1,1)],
}

def build(bp):
 for variant in ['new','tattered','abandoned']:
  for role,choices in ROLES.items():
   entries=[]
   for name,weight,lo,hi in choices:
    entries.append({'type':'item','name':name if ':' in name else 'minecraft:'+name,'weight':weight,
                    'functions':[{'function':'set_count','count':{'min':lo,'max':hi}}]})
   entries.append({'type':'empty','weight':3 if variant=='new' else 7 if variant=='tattered' else 16})
   pools=[{'rolls':{'min':2,'max':6 if role in ['vault','cargo'] else 5},'entries':entries}]
   if role in ['vault','captain','salvage']:
    pools.append({'rolls':1,'entries':[{'type':'empty','weight':90},
      {'type':'item','name':'minecraft:diamond','weight':6,'functions':[{'function':'set_count','count':{'min':1,'max':2}}]},
      {'type':'item','name':'minecraft:heart_of_the_sea','weight':1},
      {'type':'item','name':'minecraft:golden_apple','weight':3}]})
   save(bp/f'loot_tables/ships/{variant}_{role}.json',{'pools':pools})
