from numpy import ceil
from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period, parameters):
        return add(person, period, "e00900", "e02100", "k1bx14")


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    label = "sey for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("sey", tax_unit, period)


class niit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Net Investment Income Tax from Form 8960"""


class combined(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sum of iitax and payrolltax"""

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "iitax", "payrolltax")


class filer_earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("earned", tax_unit, period)


class earned(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(person, period, parameters):
        ald = parameters(period).irs.ald
        adjustment = (
            (1.0 - ald.misc.self_emp_tax_adj)
            * ald.misc.employer_share
            * person("setax", period)
        )
        return max_(0, add(person, period, "e00200", "setax") - adjustment)


class was_plus_sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(person, period, parameters):
        return person("gross_was", period) + max_(
            0,
            person("sey", period)
            * person.tax_unit("sey_frac_for_extra_oasdi", period),
        )


class eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Earned Income Credit"""

    def formula(tax_unit, period, parameters):
        return tax_unit("c59660", period)


class rptc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for filing unit"""


class rptc_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for taxpayer"""


class rptc_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for spouse"""


class exact(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class expanded_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Broad income measure that includes benefit_value_total"""
    )

    def formula(tax_unit, period, parameters):
        FILER_COMPONENTS = (
            "e00200",
            "pencon",
            "e00300",
            "e00400",
            "e00600",
            "e00700",
            "e00800",
            "e00900",
            "e01100",
            "e01200",
            "e01400",
            "e01500",
            "e02000",
            "e02100",
            "p22250",
            "p23250",
            "cmbtp",
        )
        filer_components = add(
            tax_unit,
            period,
            *[f"filer_{component}" for component in FILER_COMPONENTS],
        )
        return (
            filer_components
            + 0.5 * tax_unit("ptax_was", period)
            + tax_unit("benefit_value_total", period)
        )


class iitax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output"""

    def formula(tax_unit, period, parameters):
        return tax_unit("c09200", period) - tax_unit("refund", period)


class num(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """2 when MARS is 2 (married filing jointly); otherwise 1"""
    )


class othertaxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)"""


class payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)"""

    def formula(tax_unit, period):
        return add(
            tax_unit, period, "ptax_was", "filer_setax", "extra_payrolltax"
        )


class employee_payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Employee's share of payroll tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit("payrolltax", period) * 0.5


class refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total refundable income tax credits"""

    def formula(tax_unit, period, parameters):
        ctc_refundable = parameters(
            period
        ).irs.credits.child_tax_credit.refundable
        ctc_refund = tax_unit("c07220", period) * ctc_refundable
        REFUND_COMPONENTS = (
            "eitc",
            "c11070",
            "c10960",
            "cdcc_refund",
            "recovery_rebate_credit",
            "personal_refundable_credit",
            "ctc_new",
            "rptc",
        )
        return add(tax_unit, period, *REFUND_COMPONENTS) + ctc_refund


class sep(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    default_value = 1
    documentation = (
        """2 when MARS is 3 (married filing separately); otherwise 1"""
    )


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """sey for the tax unit (excluding dependents)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("sey", tax_unit, period)


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        std = parameters(period).irs.deductions.standard
        mars = tax_unit("mars", period)
        midr = tax_unit("midr", period)

        c15100_if_dsi = max_(
            std.dependent.additional_earned_income
            + tax_unit("filer_earned", period),
            std.dependent.amount,
        )
        basic_if_dsi = min_(std.amount[mars], c15100_if_dsi)
        basic_if_not_dsi = where(midr, 0, std.amount[mars])
        basic_stded = where(
            tax_unit("dsi", period), basic_if_dsi, basic_if_not_dsi
        )
        return basic_stded


class aged_blind_extra_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Aged and blind standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        std = parameters(period).irs.deductions.standard
        mars = tax_unit("mars", period)
        mars_type = mars.possible_values
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = tax_unit("blind_spouse", period) * 1
        aged_head = (
            tax_unit("age_head", period) >= std.aged_or_blind.age_threshold
        ) * 1
        aged_spouse = (
            (mars == mars_type.JOINT)
            & (
                tax_unit("age_spouse", period)
                >= std.aged_or_blind.age_threshold
            )
        ) * 1
        num_extra_stded = blind_head + blind_spouse + aged_head + aged_spouse
        return num_extra_stded * std.aged_or_blind.amount[mars]


class standard(Variable):
    value_type = float
    entity = TaxUnit
    label = "Standard deduction (zero for itemizers)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Calculate basic standard deduction
        basic_stded = tax_unit("basic_standard_deduction", period)
        charity = parameters(period).irs.deductions.itemized.charity
        mars = tax_unit("mars", period)
        midr = tax_unit("midr", period)
        mars_type = mars.possible_values

        # Calculate extra standard deduction for aged and blind
        extra_stded = tax_unit("aged_blind_extra_standard_deduction", period)

        # Calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((mars == mars_type.SEPARATE) & midr, 0, standard)
        return standard + charity.allow_nonitemizers * min_(
            tax_unit("c19700", period), charity.nonitemizers_max
        )


class surtax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class taxbc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Regular tax on regular taxable income before credits"""


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Adjusted Gross Income (AGI)"""

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "ymod1", "c02500", "c02900")


class c01000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Limitation on capital losses"
    unit = "currency-USD"

    def formula(tax_unit, period, parameters):
        return max_(
            (-3000.0 / tax_unit("sep", period)), tax_unit("c23650", period)
        )


class c02500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Social security (OASDI) benefits included in AGI"""


class c02900(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "'Above the line' AGI deductions"
    unit = USD
    documentation = (
        """Total of all 'above the line' income adjustments to get AGI"""
    )

    def formula(tax_unit, period, parameters):
        misc_haircuts = parameters(period).irs.ald.misc.haircut
        BASE_HAIRCUT_VARS = ["c03260", "care_deduction"]
        FILER_HAIRCUT_VARS = [
            "e03210",
            "e03400",
            "e03500",
            "e00800",
            "e03220",
            "e03230",
            "e03240",
            "e03290",
            "e03270",
            "e03150",
            "e03300",
        ]
        haircut_vars = BASE_HAIRCUT_VARS + [
            "filer_" + i for i in FILER_HAIRCUT_VARS
        ]
        return sum(
            [
                (1 - misc_haircuts[variable]) * tax_unit(variable, period)
                for variable in haircut_vars
            ]
        )


class c03260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(tax_unit, period, parameters):
        ald = parameters(period).irs.ald
        return (
            (1.0 - ald.misc.self_emp_tax_adj)
            * ald.misc.employer_share
            * tax_unit.sum(tax_unit.members("setax", period))
        )


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Itemized deductions after phase-out"
    unit = "currency-USD"
    documentation = (
        """Itemized deductions after phase-out (zero for non-itemizers)"""
    )

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("c21060", period) - tax_unit("c21040", period))


class exemption_phaseout_start(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption phaseout start"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return parameters(period).irs.income.exemption.phaseout.start[
            tax_unit("mars", period)
        ]


class c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemptions after phase-out"""

    def formula(tax_unit, period, parameters):
        phaseout = parameters(period).irs.income.exemption.phaseout
        phaseout_start = tax_unit("exemption_phaseout_start", period)
        line_5 = max_(0, tax_unit("c00100", period) - phaseout_start)
        line_6 = line_5 / (2500 / tax_unit("sep", period))
        line_7 = phaseout.rate * line_6
        return tax_unit("pre_c04600", period) * (1 - line_7)


class qbided(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "QBI deduction"
    documentation = """Qualified Business Income (QBI) deduction"""

    def formula(tax_unit, period, parameters):
        mars = tax_unit("mars", period)
        qbinc = max_(
            0,
            add(
                tax_unit,
                period,
                "filer_e00900",
                "filer_e26270",
                "filer_e02100",
                "filer_e27200",
            ),
        )
        qbid = parameters(period).irs.deductions.qualified_business_interest
        lower_threshold = qbid.threshold.lower[mars]
        upper_threshold = lower_threshold + qbid.threshold.gap[mars]
        pre_qbid_taxinc = tax_unit("pre_qbid_taxinc", period)
        under_lower_threshold = pre_qbid_taxinc < lower_threshold
        between_thresholds = ~under_lower_threshold & (
            pre_qbid_taxinc < upper_threshold
        )
        above_upper_threshold = ~under_lower_threshold & ~between_thresholds
        income_is_qualified = tax_unit("pt_sstb_income", period)

        # Wage/capital limitations
        w2_wages = tax_unit("pt_binc_w2_wages", period)
        business_property = tax_unit("pt_ubia_property", period)
        wage_cap = w2_wages * qbid.cap.w2_wages.rate
        alt_cap = (
            w2_wages * qbid.cap.w2_wages.alt_rate
            + business_property * qbid.cap.business_property.rate
        )
        fraction_of_gap_passed = (
            pre_qbid_taxinc - lower_threshold
        ) / qbid.threshold.gap[mars]
        fraction_of_gap_unused = (
            upper_threshold - pre_qbid_taxinc
        ) / qbid.threshold.gap[mars]

        # Adjustments for qualified income under the upper threshold
        qbi_between_threshold_multiplier = where(
            income_is_qualified & between_thresholds,
            fraction_of_gap_unused,
            1.0,
        )
        max_qbid = (
            qbinc * qbid.pass_through_rate * qbi_between_threshold_multiplier
        )
        full_cap = max_(wage_cap, alt_cap) * qbi_between_threshold_multiplier

        # Adjustment for QBID where income is between the main thresholds
        adjustment = fraction_of_gap_passed * (max_qbid - full_cap)

        qbid_amount = select(
            (
                under_lower_threshold,
                between_thresholds,
                above_upper_threshold,
            ),
            (
                max_qbid,
                max_qbid - adjustment,
                where(income_is_qualified, 0, min_(max_qbid, full_cap)),
            ),
        )

        # Apply taxable income cap
        net_cg = add(tax_unit, period, "filer_e00650", "c01000")
        taxinc_cap = qbid.pass_through_rate * max_(0, pre_qbid_taxinc - net_cg)
        return min_(qbid_amount, taxinc_cap)


class c04800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable income"
    documentation = """Regular taxable income"""

    def formula(tax_unit, period, parameters):
        return max_(
            0, tax_unit("pre_qbid_taxinc", period) - tax_unit("qbided", period)
        )


class c05200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Sch X,Y,Z tax"
    unit = "currency-USD"
    documentation = """Tax amount from Sch X,Y,X tables"""

    def formula(tax_unit, period, parameters):
        # Separate non-negative taxable income into two non-negative components,
        # doing this in a way so that the components add up to taxable income
        # define pass-through income eligible for PT schedule
        individual_income = parameters(period).irs.income
        e26270 = tax_unit("filer_e26270", period)
        e00900 = tax_unit("filer_e00900", period)

        # Determine pass-through and non-pass-through income
        pt_active_gross = e00900 + e26270
        pt_active = pt_active_gross
        pt_active = min_(pt_active, e00900 + e26270)
        pt_taxinc = max_(0, pt_active)
        taxable_income = tax_unit("c04800", period)

        pt_taxinc = min_(pt_taxinc, taxable_income)
        reg_taxinc = max_(0, taxable_income - pt_taxinc)
        pt_tbase = reg_taxinc

        mars = tax_unit("mars", period)

        # Initialise regular and pass-through income tax to zero
        reg_tax = 0
        pt_tax = 0
        last_reg_threshold = 0
        last_pt_threshold = 0
        for i in range(1, 7):
            # Calculate rate applied to regular income up to the current
            # threshold (on income above the last threshold)
            reg_threshold = individual_income.bracket.thresholds[str(i)][mars]
            reg_tax += individual_income.bracket.rates[
                str(i)
            ] * amount_between(reg_taxinc, last_reg_threshold, reg_threshold)
            last_reg_threshold = reg_threshold

            # Calculate rate applied to pass-through income on in the same
            # way, but as treated as if stacked on top of regular income
            # (which is not taxed again)
            pt_threshold = (
                individual_income.pass_through.bracket.thresholds[str(i)][mars]
                - pt_tbase
            )
            pt_tax += individual_income.pass_through.bracket.rates[
                str(i)
            ] * amount_between(pt_taxinc, last_pt_threshold, pt_threshold)
            last_pt_threshold = pt_threshold

        # Calculate regular and pass-through tax above the last threshold
        reg_tax += individual_income.bracket.rates["7"] * max_(
            reg_taxinc - last_reg_threshold, 0
        )
        pt_tax += individual_income.pass_through.bracket.rates["7"] * max_(
            pt_taxinc - last_pt_threshold, 0
        )
        return reg_tax + pt_tax


class c05700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c05800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)"""


class c07100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total non-refundable credits used to reduce positive tax liability"""


class c07180(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Form 221 Nonrefundable Credit"
    unit = "currency-USD"
    documentation = """Nonrefundable credit for child and dependent care expenses from Form 2441"""

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.child_and_dep_care
        if cdcc.refundable:
            return 0
        else:
            return min_(
                max_(
                    0,
                    tax_unit("c05800", period)
                    - tax_unit("filer_e07300", period),
                ),
                tax_unit("c33200", period),
            )


class cdcc_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Form 2441 Refundable Credit"
    unit = "currency-USD"
    documentation = """Refundable credit for child and dependent care expenses from Form 2441"""

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).irs.credits.child_and_dep_care
        if cdcc.refundable:
            return tax_unit("c33200", period)
        else:
            return 0


class c07200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Schedule R credit for the elderly and the disabled"""


class c07220(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (adjusted) from Form 8812"""


class c07230(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Education tax credits non-refundable amount from Form 8863 (includes c87668)"""


class c07240(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07400(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c08000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"""


class c09600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) liability"""


class c10960(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """American Opportunity Credit refundable amount from Form 8863"""
    )


class c11070(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (refunded) from Form 8812"""


class c17000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medical expense deduction"
    unit = "currency-USD"
    documentation = """Sch A: Medical expenses deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        medical = parameters(period).irs.deductions.itemized.medical
        has_aged = (tax_unit("age_head", period) >= 65) | (
            tax_unit("tax_unit_is_joint", period)
            & (tax_unit("age_spouse", period) >= 65)
        )
        medical_floor_ratio = (
            medical.floor.base + has_aged * medical.floor.aged_addition
        )
        medical_floor = medical_floor_ratio * max_(
            tax_unit("c00100", period), 0
        )
        return max_(
            0,
            tax_unit("filer_e17500", period) - medical_floor,
        )


class c18300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "SALT deduction"
    unit = "currency-USD"
    documentation = """Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        c18400 = max_(tax_unit("filer_e18400", period), 0)
        c18500 = tax_unit("filer_e18500", period)
        salt = parameters(period).irs.deductions.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("mars", period)]
        return min_(c18400 + c18500, cap)


class c19200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Interest deduction"
    unit = "currency-USD"
    documentation = """Sch A: Interest deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        return tax_unit("filer_e19200", period)


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Charitable deduction"
    unit = "currency-USD"
    documentation = """Sch A: Charity contributions deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        charity = parameters(period).irs.deductions.itemized.charity
        posagi = tax_unit("posagi", period)
        lim30 = min_(
            charity.ceiling.non_cash * posagi,
            tax_unit("filer_e20100", period),
        )
        c19700 = min_(
            charity.ceiling.all * posagi,
            lim30 + tax_unit("filer_e19800", period),
        )
        return max_(c19700, 0)


class c20500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Casualty deduction"
    unit = "currency-USD"
    documentation = """Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        casualty = parameters(period).irs.deductions.itemized.casualty
        floor = casualty.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_g20500", period) - floor)
        return deduction * (1 - casualty.haircut)


class c20800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Miscellaneous deductions"
    unit = "currency-USD"
    documentation = """Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)"""

    def formula(tax_unit, period, parameters):
        misc = parameters(period).irs.deductions.itemized.misc
        floor = misc.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_e20400", period) - floor)
        return deduction * (1 - misc.haircut)


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Phased-out itemized deductions"
    unit = "currency-USD"
    documentation = """Itemized deductions that are phased out"""

    def formula(tax_unit, period, parameters):
        nonlimited = add(tax_unit, period, "c17000", "c20500")
        phaseout = parameters(period).irs.deductions.itemized.phaseout
        mars = tax_unit("mars", period)
        c21060 = tax_unit("c21060", period)
        phaseout_amount_cap = phaseout.cap * max_(0, c21060 - nonlimited)
        uncapped_phaseout = max_(
            0,
            (
                (tax_unit("posagi", period) - phaseout.start[mars])
                * phaseout.rate
            ),
        )
        return min_(
            uncapped_phaseout,
            phaseout_amount_cap,
        )


class c21060(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Gross itemized deductions"
    unit = "currency-USD"
    documentation = (
        """Itemized deductions before phase-out (zero for non-itemizers)"""
    )

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            "c17000",
            "c18300",
            "c19200",
            "c19700",
            "c20500",
            "c20800",
        )


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net capital gains"
    unit = "currency-USD"
    documentation = "Net capital gains (long and short term) before exclusion"

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, "filer_p23250", "filer_p22250")


class tax_unit_is_joint(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Joint-filing tax unit"
    documentation = "Whether this tax unit is a joint filer."
    definition_period = YEAR


class c59660(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "EITC"
    unit = "currency-USD"
    documentation = "The Earned Income Tax Credit eligible amount."

    def formula(tax_unit, period, parameters):
        eitc = parameters(period).irs.credits.eitc
        earnings = tax_unit("filer_earned", period)
        phased_in_amount = eitc.phasein_rate * earnings
        highest_income_variable = max_(earnings, tax_unit("c00100", period))
        is_joint = tax_unit("tax_unit_is_joint", period)
        phaseout_start = (
            eitc.phaseout.start + is_joint * eitc.phaseout.joint_bonus
        )
        amount_over_phaseout = max_(
            0, highest_income_variable - phaseout_start
        )
        max_with_phaseout = max_(
            0, eitc.max - eitc.phaseout.rate * amount_over_phaseout
        )
        amount_with_phasein = min_(phased_in_amount, eitc.max)
        amount = min_(amount_with_phasein, max_with_phaseout)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_age_is_eligible = (
            eitc.eligibility.age.min <= age_head <= eitc.eligibility.age.max
        )
        spouse_age_is_eligible = is_joint * (
            eitc.eligibility.age.min <= age_spouse <= eitc.eligibility.age.max
        )
        inferred_eligibility = (
            (age_head == 0)
            | (age_spouse == 0)
            | head_age_is_eligible
            | spouse_age_is_eligible
        )
        investment_income = (
            add(
                tax_unit,
                period,
                "filer_e00400",
                "filer_e00300",
                "filer_e00600",
            )
            + max_(0, tax_unit("c01000", period))
            + max_(
                0,
                tax_unit("filer_e02000", period)
                - tax_unit("filer_e26270", period),
            )
        )
        eligible = ((tax_unit("eic", period) > 0) | inferred_eligibility) & (
            investment_income <= eitc.phaseout.max_investment_income
        )
        return eligible * amount


class c62100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) taxable income"""


class c87668(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)"""


class care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ctc_new(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class odc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other Dependent Credit"""


class personal_refundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal refundable credit"""


class recovery_rebate_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Recovery Rebate Credit, from American Rescue Plan Act of 2021"""
    )


class personal_nonrefundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal nonrefundable credit"""


class charity_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Credit for charitable giving"""


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class fstax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class invinc_agi_ec(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exclusion of investment income from AGI"
    unit = "currency-USD"
    documentation = (
        "Always equal to zero (will be removed in a future version)"
    )
    definition_period = YEAR


class invinc_ec_base(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI investment income exclusion"
    unit = "currency-USD"
    documentation = """Exclusion of investment income from AGI"""

    def formula(tax_unit, period, parameters):
        # Limitation on net short-term and
        # long-term capital losses
        limited_capital_gain = max_(
            -3000.0 / tax_unit("sep", period),
            add(tax_unit, period, "filer_p22250", "filer_p23250"),
        )
        OTHER_INV_INCOME_VARS = ["e00300", "e00600", "e01100", "e01200"]
        other_inv_income = add(
            tax_unit,
            period,
            *["filer_" + variable for variable in OTHER_INV_INCOME_VARS],
        )
        return limited_capital_gain + other_inv_income


class pre_c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemption before phase-out"""

    def formula(tax_unit, period, parameters):
        exemption = parameters(period).irs.income.exemption
        return where(
            tax_unit("dsi", period),
            0,
            tax_unit("xtot", period) * exemption.amount,
        )


class codtc_limited(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ptax_amc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Additional Medicare Tax from Form 8959 (included in payrolltax)"""
    )


class ptax_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)"""

    def formula(tax_unit, period):
        return add(
            tax_unit,
            period,
            "filer_ptax_ss_was",
            "filer_setax_ss",
            "extra_payrolltax",
        )


class ptax_was(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI + HI FICA tax"""

    def formula(tax_unit, period, parameters):
        ptax_was = add(
            tax_unit,
            period,
            "filer_ptax_ss_was",
            "filer_ptax_mc_was",
        )
        return ptax_was


class filer_setax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employment tax for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("setax", tax_unit, period)


class ymod(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI benefit tax variable"
    documentation = "Variable that is used in OASDI benefit taxation logic"
    unit = "currency-USD"

    def formula(tax_unit, period, parameters):
        ymod2 = (
            tax_unit("filer_e00400", period)
            + (0.5 * tax_unit("filer_e02400", period))
            - tax_unit("c02900", period)
        )
        ymod3 = add(
            tax_unit, period, "filer_e03210", "filer_e03230", "filer_e03240"
        )
        return tax_unit("ymod1", period) + ymod2 + ymod3


class ymod1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AGI increase"
    documentation = "Variable that is included in AGI"

    def formula(tax_unit, period, parameters):
        DIRECT_INPUTS = (
            "e00200",
            "e00700",
            "e00800",
            "e01400",
            "e01700",
            "e02100",
            "e02300",
        )
        direct_inputs = add(
            tax_unit,
            period,
            *["filer_" + variable for variable in DIRECT_INPUTS],
        )
        INVESTMENT_INCOME_SOURCES = (
            "e00300",
            "e00600",
            "e01100",
            "e01200",
        )
        investment_income = (
            add(
                tax_unit,
                period,
                *[
                    "filer_" + variable
                    for variable in INVESTMENT_INCOME_SOURCES
                ],
            )
            + tax_unit("c01000", period)
        )
        business_losses = add(tax_unit, period, "filer_e00900", "filer_e02000")
        max_business_losses = parameters(
            period
        ).irs.ald.misc.max_business_losses[tax_unit("mars", period)]
        return (
            direct_inputs
            + investment_income
            - min_(business_losses, max_business_losses)
        )


class ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Universal Basic Income benefit for filing unit"""


class taxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit included in AGI"""


class nontaxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit excluded from AGI"""


class aftertax_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "After-tax income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        expanded = tax_unit("expanded_income", period)
        combined_tax = tax_unit("combined", period)
        return expanded - combined_tax


class benefit_value_total(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total benefit value"
    definition_period = YEAR
