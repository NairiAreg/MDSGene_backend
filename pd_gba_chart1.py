import matplotlib.pyplot as plt
import numpy as np

# Данные из скрипта
categories = ['Bradykinesia', 'Rigidity', 'Tremor rest', 'Postural instability',
              'Gait difficulties falls', 'Dyskinesia', 'Motor fluctuations',
              'Dystonia', 'Cognitive decline', 'Depression', 'Psychotic',
              'Impulsive control disorder', 'Intellectual disability',
              'Autonomic', 'Olfaction', 'Seizures', 'Myoclonus', 'Primitive reflexes']

present_values = [12058, 107, 67, 55, 63, 51, 39, 17, 171, 56, 16, 7, 0, 30, 12, 1, 3, 0]
absent_values = [0, 0, 13, 16, 6, 29, 16, 28, 105, 19, 7, 0, 0, 9, 16, 0, 0, 0]
unknown_values = [0, 11951, 11978, 11987, 11989, 11978, 12003, 12013, 11782, 11983, 12035, 12051, 12058, 12019, 12030, 12057, 12055, 12058]

# Создание графика с разрывом оси (break axis)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))

# Ширина столбцов
width = 0.25
x = np.arange(len(categories))

# Построение графиков для каждой группы
ax1.bar(x - width, present_values, width, label='Present', color='#ac202d')
ax1.bar(x, absent_values, width, label='Absent', color='#154789')
ax1.bar(x + width, unknown_values, width, label='Unknown', color='#999999')

ax2.bar(x - width, present_values, width, color='#ac202d')
ax2.bar(x, absent_values, width, color='#154789')
ax2.bar(x + width, unknown_values, width, color='#999999')

# Установка пределов по оси Y для разрыва
ax1.set_ylim(5000, 13000)  # Основной верхний график
ax2.set_ylim(0, 500)  # Малые значения на нижнем графике

# Применение разрыва оси
ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.tick_params(labeltop=False)  # Убрать метки на верхнем графике
ax2.tick_params(labeltop=False)  # Убрать метки на нижнем графике

# Зигзаг для обозначения разрыва
d = .015
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)

kwargs.update(transform=ax2.transAxes)  # Переместить линии на вторую ось
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

# Добавление подписей к осям и легенды
ax2.set_xlabel('Reported signs and symptoms')
ax1.set_ylabel('Number of patients')
ax2.set_ylabel('Number of patients')

ax1.set_title('Reported signs and symptoms grouped by Present, Absent, and Unknown')

ax2.set_xticks(x)
ax2.set_xticklabels(categories, rotation=45, ha="right")

# Перемещение легенды вниз
fig.legend(loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=3)

# Показываем график
plt.tight_layout()
plt.show()
