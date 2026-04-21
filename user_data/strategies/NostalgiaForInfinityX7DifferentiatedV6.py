from NostalgiaForInfinityX7DifferentiatedV4 import NostalgiaForInfinityX7DifferentiatedV4


class NostalgiaForInfinityX7DifferentiatedV6(NostalgiaForInfinityX7DifferentiatedV4):
  """
  Minimal repair of V4:
  keep the differentiated execution behavior,
  but remove ICP from grind mode coins to test whether the large ICP stop-loss
  was the main source of tail-risk.
  """

  grind_mode_coins = [coin for coin in NostalgiaForInfinityX7DifferentiatedV4.grind_mode_coins if coin != "ICP"]
