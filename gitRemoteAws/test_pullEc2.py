# more of an integration test
def test_getAwsCat():
  from gitRemoteAws import pull_ec2
  import tempfile
  dirpath = tempfile.mkdtemp()
  #print("tempfile.mkdtemp", dirpath)
  fn = {'awsCat': dirpath}

  pull_ec2.get_awsCat(fn)
  # no assertions here, just that there are no exceptions


def test_t3cSmallerFamilyNone():
  from gitRemoteAws import pull_ec2
  ec2catalog = pull_ec2.EC2INSTANCESINFO

  import tempfile
  dirpath = tempfile.mkdtemp()
  #print("tempfile.mkdtemp", dirpath)
  fn = {'awsCat': dirpath}

  ecg = pull_ec2.Ec2CatGetter(fn)
  r_json, df_json = ecg.t0_raw(ec2catalog)
  df_pd, df_json = ecg.t1_processed(r_json)
  #ecg.t3a_smaller_familyL1(df_pd)
  #ecg.t3b_smaller_familyL2(df_pd)
  df_l3 = ecg.t3c_smaller_familyNone(df_pd)

  # no dupes in merge leading to something like 50k rows
  assert df_l3.shape[0] < 500

  # example
  # https://www.reddit.com/r/aws/comments/8bwiri/automated_cost_savings_calculator_by_upgrading/
  df_item = df_l3.loc['m','m4','m4.2xlarge'].iloc[0]
  assert df_item.type_smaller == 'm5a.xlarge'
  assert df_item.type_same_cheaper == 'm5a.2xlarge'

  # t2.micro should go to nano at least
  df_item = df_l3.loc['t','t2','t2.micro'].iloc[0]
  assert df_item.type_smaller == 't3a.nano'
