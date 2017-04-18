import pandas as pd
from .utils import create_address_fields


def test_create_address_fields():
    sbe_data = pd.DataFrame({
        'mail_addr1': pd.Series([
            '3523 N ROXBORO ST # 3H',
            '111 E CHANNING AVE',
            '801 LORAINE AVE',
            '707 EAST HUDSON AVE',
            '53 MOXY HUDSON AVE'
            # '116 � E EDGEWOOD DR'
        ])
    })
    create_address_fields(sbe_data, 'mail_addr1')
    assert list(sbe_data['clean_street_number']) == ['3523', '111', '801', '707', '53']
    assert list(sbe_data['clean_street_name']) == ['ROXBORO', 'CHANNING', 'LORAINE', 'HUDSON', 'MOXY HUDSON']
    assert list(sbe_data['clean_street_directional']) == ['N', 'E', '', 'E', '']
    assert list(sbe_data['clean_street_type']) == ['ST', 'AVE', 'AVE', 'AVE', 'AVE']
    assert list(sbe_data['clean_street_apartment']) == ['3H', '', '', '', '']