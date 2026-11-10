"""English display labels; the sealed study's internal artifact schemas stay unchanged."""
from bs4 import BeautifulSoup
import pandas as pd
from pandas.io.formats.style import Styler
from IPython.display import display as _display, HTML

LABELS = {
 'Naïf':'Naive baseline', 'Logistique':'Logistic regression', 'Forêt':'Random forest',
 'Forêt sigmoid':'Random forest (sigmoid)', 'Logistique sigmoid':'Logistic regression (sigmoid)',
 'Aucun contact':'No contact', 'Aléatoire':'Random', 'Métier':'Business rule', 'Prédictif':'Predictive',
 'type':'Data type', 'manquants':'Missing', 'modalités':'Unique values', 'effectif':'Count',
 'lignes':'Rows', 'colonnes':'Columns', 'doublons_exacts':'Exact duplicates',
 'clients_repetes':'Repeated customer IDs', 'numeros_repetes':'Repeated row numbers',
 'score_domaine_large':'Credit score within broad range', 'age_adulte_plausible':'Plausible adult age',
 'anciennete_plausible':'Plausible tenure', 'solde_non_negatif':'Non-negative balance',
 'salaire_non_negatif':'Non-negative salary', 'produits_entiers_positifs':'Positive integer product count',
 'carte_binaire':'Binary card indicator', 'activite_binaire':'Binary activity indicator',
 'pays_attendus':'Expected country categories', 'genre_observe':'Observed gender categories',
 'brut':'Raw', 'préparé':'Prepared', 'colonnes (clé technique incluse)':'Columns (including technical key)',
 'valeurs modifiées':'Modified values', 'clients':'Customers', 'audit':'Audit',
 'moyenne':'Mean', 'écart-type':'Standard deviation', 'minimum':'Minimum', 'maximum':'Maximum',
 'variable':'Variable', 'segment':'Segment', 'n':'n', 'departs':'Churn labels',
 'proportion':'Churn proportion', 'ic95_bas':'95% CI lower', 'ic95_haut':'95% CI upper',
 'Solde nul':'Zero balance', 'Solde positif':'Positive balance',
 'positifs':'Positive labels','modele':'Model','roc_auc':'ROC-AUC','average_precision':'Average precision',
 'brier':'Brier score','contacts':'Contacts','departs_contactes':'Churn labels targeted',
 'precision_budget':'Precision at budget','rappel_budget':'Recall at budget','lift_budget':'Lift at budget',
 'probabilite_moyenne':'Mean predicted probability','prevalence':'Prevalence',
 'intervalle':'Score interval','probabilite':'Mean predicted probability','observe':'Observed proportion',
 'IC95 bas':'95% CI lower','IC95 haut':'95% CI upper',
 'strategie':'Strategy','population':'Population','positifs_population':'Population positive labels',
 'precision':'Precision','rappel':'Recall','lift':'Lift','cout_scenario_eur':'Scenario cost (USD)',
 'gain_net_scenario_eur':'Scenario net gain (USD)',
 'Activité':'Activity','Âge':'Age','Produits':'Products','Inactif':'Inactive','Actif':'Active',
 'Groupe':'Group','Clients train':'Training customers','Labels départ':'Churn labels',
 'Part départ':'Churn proportion','IC 95 % bas':'95% CI lower','IC 95 % haut':'95% CI upper',
 'Stratégie':'Strategy','Labels départ ciblés':'Churn labels targeted','Précision':'Precision',
 'Rappel':'Recall','Coût hypothétique (USD)':'Hypothetical cost (USD)',
 'Labels ciblés':'Labels targeted','Départs évités supposés':'Assumed departures prevented',
 'Coût scénario (USD)':'Scenario cost (USD)','Gain net scénario (USD)':'Scenario net gain (USD)',
 'q au point mort':'Break-even q','Fraction supposée de départs évités q':'Assumed fraction of departures prevented q',
}

def en(value):
    """Translate a display label without mutating an analytical object."""
    if not isinstance(value, str):
        return value
    if value.startswith('texte_sans_espaces_'):
        return 'Non-empty, trimmed text: ' + value[len('texte_sans_espaces_'):]
    if value.startswith('fini_'):
        return 'Finite values: ' + value[len('fini_'):]
    return LABELS.get(value, value)


def display(*objects, **kwargs):
    """Render English table labels while retaining original data and numeric formatting."""
    for obj in objects:
        if isinstance(obj, pd.Series):
            obj = obj.to_frame()
        if isinstance(obj, (pd.DataFrame, Styler)):
            markup = obj.to_html()
            soup = BeautifulSoup(markup, 'html.parser')
            for node in list(soup.find_all(string=True)):
                if node.parent.name in {'style', 'script'}:
                    continue
                raw = str(node)
                translated = en(raw.strip())
                if translated != raw.strip():
                    node.replace_with(raw.replace(raw.strip(), translated))
            _display(HTML(str(soup)), **kwargs)
        else:
            _display(obj, **kwargs)


def segment_rate_figure(segments, variables, overall_rate, *, title):
    """Show nominal groups horizontally and ordered groups in their natural order.

    Only renders existing training aggregates; does not calculate or select segments.
    """
    import math
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, PercentFormatter

    orders = {
        'Geography': ['France', 'Germany', 'Spain'],
        'Gender': ['Female', 'Male'],
        'IsActiveMember': ['1', '0'],
        'ZeroBalance': ['Solde nul', 'Solde positif'],
        'AgeBand': ['18–34', '35–44', '45–54', '55+'],
        'NumOfProducts': ['1', '2', '3', '4'],
    }
    titles = {'Geography': 'Country', 'Gender': 'Gender',
              'IsActiveMember': 'Membership activity', 'ZeroBalance': 'Account balance',
              'AgeBand': 'Age group (years)', 'NumOfProducts': 'Number of products'}
    names = {'IsActiveMember': {'1': 'Active', '0': 'Inactive'},
             'ZeroBalance': {'Solde nul': 'Zero balance', 'Solde positif': 'Positive balance'}}
    ordered = {'AgeBand', 'NumOfProducts'}
    nominal = segments[segments.variable.isin([v for v in variables if v not in ordered])]
    nominal_limit = min(1.08, max(.3, math.ceil((nominal.ic95_haut.max() + .08) * 10) / 10)) if len(nominal) else 1
    ncols = min(2, len(variables))
    nrows = math.ceil(len(variables) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.8 * ncols, 3.7 * nrows + .8),
                             squeeze=False, layout='constrained')
    for ax, variable in zip(axes.flat, variables):
        group = segments.loc[segments.variable.eq(variable)].copy()
        group['segment'] = group.segment.astype(str)
        group = group.set_index('segment').loc[orders[variable]].reset_index()
        labels = [names.get(variable, {}).get(row.segment, row.segment) for row in group.itertuples()]
        values = group.proportion.to_numpy()
        lower = np.maximum(0, values - group.ic95_bas.to_numpy())
        upper = np.maximum(0, group.ic95_haut.to_numpy() - values)
        colors = ['#c17b22' if n < 100 else '#267985' for n in group.n]
        positions = np.arange(len(group))
        if variable in ordered:
            ax.bar(positions, values, width=.58, color=colors,
                   yerr=[lower, upper], capsize=4, error_kw={'ecolor': '#283e45', 'elinewidth': 1})
            ax.axhline(overall_rate, color='#69767b', linestyle='--', linewidth=1)
            ax.set_xticks(positions, [f'{label}\nn = {n:,}' for label, n in zip(labels, group.n)])
            ax.set_ylim(0, 1.08)
            ax.yaxis.set_major_locator(FixedLocator(np.arange(0, 1.01, .2)))
            ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
            ax.set_ylabel('Observed churn proportion')
            ax.grid(axis='y', alpha=.15)
            for x, row in zip(positions, group.itertuples()):
                ax.text(x, row.ic95_haut + .025, f'{row.proportion:.1%}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')
        else:
            ax.barh(positions, values, height=.48, color=colors,
                    xerr=[lower, upper], capsize=4, error_kw={'ecolor': '#283e45', 'elinewidth': 1})
            ax.axvline(overall_rate, color='#69767b', linestyle='--', linewidth=1)
            ax.set_yticks(positions, [f'{label}  (n = {n:,})' for label, n in zip(labels, group.n)])
            ax.invert_yaxis()
            ax.set_xlim(0, nominal_limit)
            ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
            ax.set_xlabel('Observed churn proportion')
            ax.grid(axis='x', alpha=.15)
            for y, row in zip(positions, group.itertuples()):
                ax.text(row.ic95_haut + nominal_limit * .025, y, f'{row.proportion:.1%}',
                        va='center', fontsize=11, fontweight='bold')
        ax.set_title(titles[variable], fontsize=12, fontweight='bold', pad=12)
        ax.set_axisbelow(True)
        ax.spines[['top', 'right']].set_visible(False)
    for ax in list(axes.flat)[len(variables):]:
        ax.set_visible(False)
    fig.suptitle(f'{title}\nDashed line: training mean {overall_rate:.1%} · whiskers: 95% Wilson CI', fontsize=14)
    note = 'n = training customers'
    if (segments.loc[segments.variable.isin(variables), 'n'] < 100).any():
        note += ' · amber bars: fewer than 100 customers; interpret with caution'
    fig.supxlabel(note, fontsize=9, color='#526670')
    return fig, axes
