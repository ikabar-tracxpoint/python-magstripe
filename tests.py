import unittest
from magstripe import MagStripe, MagStripeError


class MagStripeTests(unittest.TestCase):
    valid_strings = [
        '%B4242424242424242^SURNAME/FIRSTNAME I^15052011000000000000?;4242424242424242=15052011000000000000?',
        '%B4242424242424242^SURNAME/FIRSTNAME I^15052011000000000000?;4242424242424242=15052011000000000000?;999999999999999997387619999999999999999999?',
        # Add every credit and debit card you can get your hands on.
    ]

    invalid_strings = [
        '',
        ';45645645645646456=4792?',
        ';5646456464564565656=12491010000000000?',
        '%63400445654646456=000078089000000000?;3454353453453545345=000078089000000000?+345345345353453434=345345345345435345345?',
        '%B212562477074168^ABCD/A MR^P 1501M                                         ^?;35345345345345345=2323?',
        '%LC/MR/ABCDEFG/A/ABCDE?;45454545454=112015?',
        '%  AA 00 00 00 A  RN^ABCDEFG ABCD ABCDE         ^                           ?',
        ';92101707137827464=2456?',
        ';00007399=?',
        '%B456475756755675^ABCDE/A MR^P 1407M                                        ^?;34534534534534534=7878?',
        ';00000000==201100100900083753?',
        ';98700223563013312=0000000000000004120?', #Shufersal member card

    ]

    def test_valid_strings(self):
        m = MagStripe()
        for s in self.valid_strings:
            self.assertTrue(isinstance(m.parse(s), dict))

    def test_invalid_strings(self):
        m = MagStripe()
        for s in self.invalid_strings:
            self.assertRaises(MagStripeError, m.parse, s)

    def test_parse(self):
        card = '%B4242424242424242^SURNAME/FIRSTNAME I^15052011000000000000?;4242424242424242=15052011000000000000?'
        m = MagStripe()
        parsed_card = m.parse(card)
        self.assertEqual(parsed_card['account'], '4242424242424242', 'Account not parsed correctly')
        self.assertEqual(parsed_card['name'], 'FIRSTNAME I SURNAME', 'Name not parsed correctly')
        self.assertEqual(parsed_card['expiry_year'], '15', 'Year not parsed correctly')
        self.assertEqual(parsed_card['expiry_month'], '05', 'Month not parsed correctly')


if __name__ == '__main__':
    unittest.main()
