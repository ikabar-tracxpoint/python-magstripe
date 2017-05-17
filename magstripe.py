import re


class MagStripeError(Exception):
    pass


class MagStripe:
    """
    For ISO 7813 financial cards. Reads track 1 and 2.
    Not sure what would happen if a 3-track card was used.
    Intended for string input from USB keyboard emulator card reader.
    Compares track 1 and 2, because redundancy.
    """

    # Track parsing based on
    # https://github.com/eighthave/pyidtech/blob/master/idtech.py
    def __init__(self):
        pass

    def parse_track1(self, trackstr):
        if not trackstr:
            raise MagStripeError('Blank track 1 data')

        if trackstr[1] != 'B':
            raise MagStripeError('Wrong track 1 format (not B)')
        track_data = trackstr[2:len(trackstr)-1]  # remove start/end sentinel

        try:
            card_number, name, data = track_data.split('^')
        except ValueError:
            raise MagStripeError('Could not parse track 1')

        try:
            last_name, first_name = name.split('/')
        except ValueError:
            raise MagStripeError('Could not parse cardholder name')

        exp_year = data[0:2]
        exp_month = data[2:4]

        if not self.validate(card_number):
            raise MagStripeError('Card number in track 1 did not validate')

        return {
            'account': card_number,
            'expiry_month': exp_month,
            'expiry_year': exp_year,
            'name': '%s %s' % (first_name.strip(), last_name.strip())
        }

    def parse_track2(self, trackstr):
        if not trackstr:
            raise MagStripeError('Blank track 2 data')
        track_data = trackstr[1:len(trackstr)]  # remove start ';'

        try:
            card_number, data = track_data.split('=')
        except ValueError:
            raise MagStripeError('Could not parse track 2')

        exp_year = data[0:2]
        exp_month = data[2:4]

        if not self.validate(card_number):
            raise MagStripeError('Card number in track 2 did not validate')

        return {
            'account': card_number,
            'expiry_month': exp_month,
            'expiry_year': exp_year
        }

    # http://atlee.ca/blog/2008/05/27/validating-credit-card-numbers-in-python/
    @staticmethod
    def validate(card_number):
        """
        Returns True if the credit card number ``cardnumber`` is valid,
        False otherwise.

        Returning True doesn't imply that a card with this number has ever
        been, or ever will be issued.

        Currently supports Visa, Mastercard, American Express, Discovery
        and Diners Cards.

        validate_cc("4111-1111-1111-1111") -> True
        validate_cc("4111 1111 1111 1112") -> False
        validate_cc("5105105105105100") -> True
        validate_cc(5105105105105100) -> True
        """
        # Strip out any non-digits
        s = re.sub("[^0-9]", "", str(card_number))
        regexps = [
            "^4\d{15}$",
            "^5[1-5]\d{14}$",
            "^3[4,7]\d{13}$",
            "^3[0,6,8]\d{12}$",
            "^6011\d{12}$",
        ]

        if not any(re.match(r, s) for r in regexps):
            return False

        checksum = 0
        x = len(s) % 2
        for i, c in enumerate(s):
            j = int(c)
            if i % 2 == x:
                k = j*2
                if k >= 10:
                    k -= 9
                checksum += k
            else:
                checksum += j
        return checksum % 10 == 0

    def parse(self, card_tracks):
        try:
            tracks = card_tracks.split('?')
        except ValueError:
            raise MagStripeError('Did not get expected track 1 and 2')

        track1 = self.parse_track1(tracks[0])
        track2 = self.parse_track2(tracks[1])

        if (track1['account'] == track2['account'] and
                track1['expiry_month'] == track2['expiry_month'] and
                track1['expiry_year'] == track2['expiry_year']):
            return track1
        else:
            raise MagStripeError('Track 1 and 2 data did not match')
