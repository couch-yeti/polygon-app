from marshmallow import Schema, fields, post_dump

class Dividend(Schema):
    ticker = fields.String()
    declaration_date = fields.Date()
    ex_dividend_date = fields.Date()
    frequency = fields.Int()
    pay_date = fields.Date()
    cash_amount = fields.Decimal(places=3)
    record_date = fields.Date()

    @post_dump
    def dynamo_record(self, data, **kwargs):
        return {
            "pk": data["pay_date"],
            "sk": data["ticker"],
            **data,
        }