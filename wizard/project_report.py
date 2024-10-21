from odoo import fields, models
from datetime import datetime

class ProjectDetail(models.TransientModel):
    _name = 'project.detail'

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    project = fields.Many2one('project.project', string="Project")

    def project_report(self):
        domain_order = []

        if self.date_from and self.date_to:
            domain_order += [('date_start', '>=', self.date_from), ('date_end', '<=', self.date_to)]

        if self.project:
            domain_order += [('id', '=', self.project.id)]

        orders = self.env['project.project'].search(domain_order)

        return {'orders': orders}

    def generate_project_report(self):
        return self.env.ref('pb_project_report.pb_report_report').report_action(self)

class ProjectProject(models.Model):
    _inherit = 'project.project'

    used_days = fields.Integer(string="Used Days", compute='_compute_used_days')
    remaining_days = fields.Integer(string="Remaining Days", compute='_compute_remaining_days')
    completed_milestone = fields.Char(string="Completed Milestone", compute='_compute_completed_milestone')
    remaining_milestone = fields.Char(string="Remaining Milestone", compute='_compute_remaining_milestone')
    tag_names = fields.Char(string="Tag Names", compute='_compute_tag_names')

    def _compute_remaining_days(self):
        for project in self:
            if project.project_duration and project.used_days:
                remaining_days = max(project.project_duration - project.used_days, 0)
                project.remaining_days = remaining_days
            else:
                project.remaining_days = 0

    def _compute_used_days(self):
        for project in self:
            if project.date_start:
                today = datetime.today().date()
                used_days = (today - project.date_start).days
                project.used_days = max(used_days, 0)
            else:
                project.used_days = 0

    def _compute_completed_milestone(self):
        for record in self:
            if record.id:
                completed_milestone_names = self.env['project.milestone'].search([
                    ('project_id', '=', record.id),
                    ('is_reached', '=', True)
                ]).mapped('name')
                record.completed_milestone = ' & '.join(completed_milestone_names)

    def _compute_remaining_milestone(self):
        for record in self:
            if record.id:
                remaining_milestone_names = self.env['project.milestone'].search([
                    ('project_id', '=', record.id),
                    ('is_reached', '=', False)
                ]).mapped('name')
                record.remaining_milestone = ' & '.join(remaining_milestone_names)

    def _compute_tag_names(self):
        for project in self:
            tag_names = " & ".join(project.tag_ids.mapped('name'))
            project.tag_names = tag_names



