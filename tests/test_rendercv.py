import unittest
from rendercv import data_model, rendering

from datetime import date as Date
from pydantic import ValidationError
from pydantic_core import Url


class TestRendercv(unittest.TestCase):
    def test_check_spelling(self):
        sentences = [
            "This is a sentence.",
            "This is a sentance with special characters &@#&^@*#&)((!@#_)()).",
            r"12312309 Thisdf sdfsd is a sentence *safds\{\}[[[]]]",
        ]

        for sentence in sentences:
            with self.subTest(sentence=sentence):
                data_model.check_spelling(sentence)

    def test_compute_time_span_string(self):
        start_date = Date(year=2020, month=1, day=1)
        end_date = Date(year=2021, month=1, day=1)
        expected = "1 year 1 month"
        result = data_model.compute_time_span_string(start_date, end_date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        start_date = Date(year=2020, month=1, day=1)
        end_date = Date(year=2020, month=2, day=1)
        expected = "1 month"
        result = data_model.compute_time_span_string(start_date, end_date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        start_date = Date(year=2020, month=1, day=1)
        end_date = Date(year=2023, month=3, day=2)
        expected = "3 years 2 months"
        result = data_model.compute_time_span_string(start_date, end_date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        start_date = Date(year=2020, month=1, day=1)
        end_date = Date(year=1982, month=1, day=1)
        with self.subTest(msg="start_date > end_date"):
            with self.assertRaises(ValueError):
                data_model.compute_time_span_string(start_date, end_date)

    def test_format_date(self):
        date = Date(year=2020, month=1, day=1)
        expected = "Jan. 2020"
        result = data_model.format_date(date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        date = Date(year=1983, month=12, day=1)
        expected = "Dec. 1983"
        result = data_model.format_date(date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        date = Date(year=2045, month=6, day=1)
        expected = "June 2045"
        result = data_model.format_date(date)
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

    def test_data_event_check_dates(self):
        # Inputs with valid dates:
        inputs = [
            {
                "start_date": Date(year=2020, month=1, day=1),
                "end_date": Date(year=2021, month=1, day=1),
            },
            {
                "start_date": Date(year=2020, month=1, day=1),
                "end_date": None,
            },
            {
                "start_date": Date(year=2020, month=1, day=1),
                "end_date": "present",
            },
            {"date": "My Birthday"},
        ]

        for input in inputs:
            with self.subTest(msg="valid dates"):
                data_model.Event(**input)

        # Inputs with invalid dates:
        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": Date(year=2019, month=1, day=1),
        }
        with self.subTest(msg="start_date > end_date"):
            with self.assertRaises(ValidationError):
                data_model.Event(**input)

        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": Date(year=2900, month=1, day=1),
        }
        with self.subTest(msg="end_date > present"):
            with self.assertRaises(ValidationError):
                data_model.Event(**input)

        # Other inputs:
        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": "present",
            "date": "My Birthday",
        }
        event = data_model.Event(**input)
        with self.subTest(msg="start_date, end_date, and date are all provided"):
            self.assertEqual(event.date, None)
            self.assertEqual(event.start_date, input["start_date"])
            self.assertEqual(event.end_date, input["end_date"])

        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": None,
            "date": "My Birthday",
        }
        event = data_model.Event(**input)
        with self.subTest(msg="start_date and date are provided"):
            self.assertEqual(event.start_date, None)
            self.assertEqual(event.end_date, None)
            self.assertEqual(event.date, input["date"])

        input = {
            "start_date": None,
            "end_date": Date(year=2020, month=1, day=1),
            "date": "My Birthday",
        }
        event = data_model.Event(**input)
        with self.subTest(msg="end_date and date are provided"):
            self.assertEqual(event.start_date, None)
            self.assertEqual(event.end_date, None)
            self.assertEqual(event.date, input["date"])

        input = {
            "start_date": None,
            "end_date": None,
            "date": "My Birthday",
        }
        event = data_model.Event(**input)
        with self.subTest(msg="only date is provided"):
            self.assertEqual(event.start_date, None)
            self.assertEqual(event.end_date, None)
            self.assertEqual(event.date, input["date"])

    def test_data_event_date_and_location_strings_with_timespan(self):
        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": Date(year=2021, month=1, day=16),
            "location": "My Location",
        }
        expected = [
            "My Location",
            "Jan. 2020 to Jan. 2021",
            "1 year 1 month",
        ]
        event = data_model.Event(**input)
        result = event.date_and_location_strings_with_timespan
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        input = {
            "date": "My Birthday",
            "location": "My Location",
        }
        expected = [
            "My Location",
            "My Birthday",
        ]
        event = data_model.Event(**input)
        result = event.date_and_location_strings_with_timespan
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

    def test_data_event_date_and_location_strings_without_timespan(self):
        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": Date(year=2021, month=1, day=16),
            "location": "My Location",
        }
        expected = [
            "My Location",
            "Jan. 2020 to Jan. 2021",
        ]
        event = data_model.Event(**input)
        result = event.date_and_location_strings_without_timespan
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        input = {
            "date": "My Birthday",
            "location": "My Location",
        }
        expected = [
            "My Location",
            "My Birthday",
        ]
        event = data_model.Event(**input)
        result = event.date_and_location_strings_without_timespan
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

    def test_data_event_highlight_strings(self):
        input = {
            "highlights": [
                "My Highlight 1",
                "My Highlight 2",
            ],
        }
        expected = [
            "My Highlight 1",
            "My Highlight 2",
        ]
        event = data_model.Event(**input)
        result = event.highlight_strings
        with self.subTest(expected=expected):
            self.assertEqual(result, expected)

        input = {}
        expected = []
        event = data_model.Event(**input)
        result = event.highlight_strings
        with self.subTest(msg="no highlights"):
            self.assertEqual(result, expected)

    def test_data_event_markdown_url(self):
        # Github link:
        input = {"url": "https://github.com/sinaatalay"}
        expected = "[view on GitHub](https://github.com/sinaatalay)"
        event = data_model.Event(**input)
        result = event.markdown_url
        with self.subTest(msg="Github link"):
            self.assertEqual(result, expected)

        # LinkedIn link:
        input = {"url": "https://www.linkedin.com/"}
        expected = "[view on LinkedIn](https://www.linkedin.com/)"
        event = data_model.Event(**input)
        result = event.markdown_url
        with self.subTest(msg="LinkedIn link"):
            self.assertEqual(result, expected)

        # Instagram link:
        input = {"url": "https://www.instagram.com/"}
        expected = "[view on Instagram](https://www.instagram.com/)"
        event = data_model.Event(**input)
        result = event.markdown_url
        with self.subTest(msg="Instagram link"):
            self.assertEqual(result, expected)

        # Youtube link:
        input = {"url": "https://www.youtube.com/"}
        expected = "[view on YouTube](https://www.youtube.com/)"
        event = data_model.Event(**input)
        result = event.markdown_url
        with self.subTest(msg="Youtube link"):
            self.assertEqual(result, expected)

        # Other links:
        input = {"url": "https://www.google.com/"}
        expected = "[view on my website](https://www.google.com/)"
        event = data_model.Event(**input)
        result = event.markdown_url
        with self.subTest(msg="Other links"):
            self.assertEqual(result, expected)

    def test_data_event_month_and_year(self):
        input = {
            "start_date": Date(year=2020, month=1, day=1),
            "end_date": Date(year=2021, month=1, day=16),
        }
        expected = None
        event = data_model.Event(**input)
        result = event.month_and_year
        with self.subTest(msg="start_date and end_date are provided"):
            self.assertEqual(result, expected)

        input = {
            "date": "My Birthday",
        }
        expected = "My Birthday"
        event = data_model.Event(**input)
        result = event.month_and_year
        with self.subTest(msg="custom date is provided"):
            self.assertEqual(result, expected)

        input = {
            "date": Date(year=2020, month=1, day=1),
        }
        expected = "Jan. 2020"
        event = data_model.Event(**input)
        result = event.month_and_year
        with self.subTest(msg="date is provided"):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
