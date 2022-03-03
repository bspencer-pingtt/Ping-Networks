from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Employee'

    bir_file_number = fields.Char('BIR File Number')
    nis_number = fields.Char('NIS Number')
    deduction_year_ids = fields.One2many('deduction.years','employee_id',string='Deduction')
    basic_salary = fields.Float('Basic Salary')
    number_of_weeks_at_8_25 = fields.Float('Number of weeks at $8.25')
    number_of_weeks_at_4_80 = fields.Float('Number of weeks at $4.80')

    # def write(self, vals):
    #     res = super(HrEmployee, self).write(vals)
    #     if vals.get('number_of_weeks_at_8_25') and self.number_of_weeks_at_4_80:
    #         raise ValidationError("You can not select Number of weeks at $8.25 and Number of weeks at $4.80 at once.")
    #
    #     if vals.get('number_of_weeks_at_4_80') and self.number_of_weeks_at_8_25:
    #         raise ValidationError("You can not select Number of weeks at $8.25 and Number of weeks at $4.80 at once.")
    #
    #     return res

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'TD4 Report-%s' % (self.name)

    def get_remuneration(self):
        return round(self.basic_salary *12)

    def get_total_deduction(self,year):

        deduction_year = self.deduction_year_ids.filtered(lambda d:d.year == str(year))

        if deduction_year:
            return deduction_year.deduction_amount
        else:
            return 0

    def calculate_gross_earnings(self):
        #Gross Earnings = Remuneration before deduction + Commissions + Taxable allowances \
        #+ Travelling + other + Income related to previous years paid in current year + \
        # Savings Plan withdrawals of Contributions made by company.

        gross_earning = (self.basic_salary * 12) + 0 + 0 + 0 + 0 + 0 + 0 + 0

        return round(gross_earning)

    def get_national_insurance_deduction(self,weeks):
        #National Insurance deducted = Employee's weekly contribution rate x number of
        #the 52 weeks worked (Round to nearest) No cent value.

        contribution_rate = 0
        basic_salary = self.basic_salary

        contribution_rate_obj = self.env['national.insurance.contribution'].search([])

        for rate in contribution_rate_obj:
            range = [int(i) for i in rate.earning_range.split('-')]

            range_from = range[0]
            range_to = range[1]
            if basic_salary > range_from and basic_salary < range_to:
                contribution_rate = rate.contribution_rate
                break


        weekly_contribution_rate = contribution_rate * int(weeks)

        return round(weekly_contribution_rate)

    def get_income_tax_diduction(self,gross_earning,total_deduction_as_per_td1):
        #Gross Earnings - Total Deductions as per TD1 * 0.25

        income_tax_deduction = (gross_earning - total_deduction_as_per_td1) * 0.25

        return round(income_tax_deduction)

    def get_health_surcharge_deducted(self):
        #Number of weeks at $8.25 or Number of weeks at $4.80
        # if self.number_of_weeks_at_8_25:
        #     return round(int(weeks) * 8.25)
        # elif self.number_of_weeks_at_4_80:
        #     return round(int(weeks) * 4.80)
        # else:
        #     return 0
        return round((self.number_of_weeks_at_8_25 * 8.25) + (self.number_of_weeks_at_4_80 * 4.80))



class DeductionYears(models.Model):
    _name = 'deduction.years'
    _description = 'Deduction Years'

    def _get_years(self):
        return [(str(i), i) for i in range(2020 ,fields.Date.today().year + 10 , 1)]

    year = fields.Selection(selection='_get_years', string='Year', required=True,
                            default=lambda x: str(fields.Date.today().year - 1))

    deduction_amount = fields.Float('Deduction',required=True)
    employee_id = fields.Many2one('hr.employee')

class NationalInsuranceContribution(models.Model):
    _name = 'national.insurance.contribution'

    earning_range = fields.Char('Monthly Earnings')
    contribution_rate = fields.Float("Employee's weekly contribution rate")
