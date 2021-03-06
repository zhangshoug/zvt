# -*- coding: utf-8 -*-
from zvdata import IntervalLevel
from zvt.factors.ma.ma_factor import CrossMaFactor
from zvt.factors.target_selector import TargetSelector
from zvt.factors.technical_factor import BullFactor
from ..context import init_test_context

init_test_context()


class TechnicalSelector(TargetSelector):

    def __init__(self, entity_ids=None, entity_type='stock', exchanges=['sh', 'sz'], codes=None, the_timestamp=None,
                 start_timestamp=None, end_timestamp=None, long_threshold=0.8, short_threshold=0.2,
                 level=IntervalLevel.LEVEL_1DAY, provider='joinquant') -> None:
        super().__init__(entity_ids, entity_type, exchanges, codes, the_timestamp, start_timestamp, end_timestamp,
                         long_threshold, short_threshold, level, provider)

    def init_factors(self, entity_ids, entity_type, exchanges, codes, the_timestamp, start_timestamp,
                     end_timestamp, level):
        bull_factor = BullFactor(entity_ids=entity_ids, entity_type=entity_type, exchanges=exchanges,
                                 codes=codes, the_timestamp=the_timestamp, start_timestamp=start_timestamp,
                                 end_timestamp=end_timestamp, provider='joinquant', level=level)

        self.filter_factors = [bull_factor]


def test_cross_ma_selector():
    entity_ids = ['stock_sz_000338']
    entity_type = 'stock'
    start_timestamp = '2018-01-01'
    end_timestamp = '2019-06-30'
    my_selector = TargetSelector(entity_ids=entity_ids,
                                 entity_type=entity_type,
                                 start_timestamp=start_timestamp,
                                 end_timestamp=end_timestamp)
    # add the factors
    my_selector \
        .add_filter_factor(CrossMaFactor(entity_ids=entity_ids,
                                         entity_type=entity_type,
                                         start_timestamp=start_timestamp,
                                         end_timestamp=end_timestamp,
                                         computing_window=10,
                                         windows=[5,10],
                                         persist_factor=False,
                                         level=IntervalLevel.LEVEL_1DAY))
    my_selector.run()
    print(my_selector.open_long_df)
    print(my_selector.open_short_df)
    assert 'stock_sz_000338' in my_selector.get_open_short_targets('2018-01-29')


def test_technical_selector():
    selector = TechnicalSelector(entity_type='stock', start_timestamp='2019-01-01',
                                 end_timestamp='2019-06-10',
                                 level=IntervalLevel.LEVEL_1DAY,
                                 provider='joinquant')

    selector.run()

    print(selector.get_result_df())

    targets = selector.get_open_long_targets('2019-06-04')

    assert 'stock_sz_000338' not in targets
    assert 'stock_sz_000338' not in targets
    assert 'stock_sz_002572' not in targets
    assert 'stock_sz_002572' not in targets

    targets = selector.get_open_short_targets('2019-06-04')
    assert 'stock_sz_000338' in targets
    assert 'stock_sz_000338' in targets
    assert 'stock_sz_002572' in targets
    assert 'stock_sz_002572' in targets

    selector.move_on(timeout=0)

    targets = selector.get_open_long_targets('2019-06-19')

    assert 'stock_sz_000338' in targets

    assert 'stock_sz_002572' not in targets
