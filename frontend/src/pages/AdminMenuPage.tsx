import { useEffect, useState, type FormEvent } from 'react';
import {
  createAdminDish,
  disableAdminDish,
  fetchAdminDishes,
  fetchCategories,
  updateAdminDish,
} from '../api/menu';
import { PageLayout } from '../components/layout/PageLayout';
import type { Category, Dish, DishUpsertInput } from '../types/menu';
import { getApiErrorMessage } from '../utils/api';
import { formatCurrency } from '../utils/format';

type Notice = {
  tone: 'success' | 'error' | 'info';
  text: string;
};

type DishDraft = {
  name: string;
  description: string;
  price: string;
  categoryId: string;
  isActive: boolean;
  isAvailable: boolean;
};

function createEmptyDraft(categories: Category[]): DishDraft {
  return {
    name: '',
    description: '',
    price: '',
    categoryId: categories[0] ? String(categories[0].id) : '',
    isActive: true,
    isAvailable: true,
  };
}

function createDraftFromDish(dish: Dish): DishDraft {
  return {
    name: dish.name,
    description: dish.description,
    price: dish.price.toString(),
    categoryId: String(dish.category),
    isActive: dish.isActive,
    isAvailable: dish.isAvailable,
  };
}

function sortDishes(dishes: Dish[]) {
  return [...dishes].sort((left, right) => {
    if (left.isActive !== right.isActive) {
      return left.isActive ? -1 : 1;
    }

    if (left.categoryName !== right.categoryName) {
      return left.categoryName.localeCompare(right.categoryName);
    }

    return left.name.localeCompare(right.name);
  });
}

function getDishStatusLabel(dish: Dish) {
  if (!dish.isActive) {
    return 'Disabilitato';
  }

  return dish.isAvailable ? 'Disponibile' : 'Esaurito';
}

export function AdminMenuPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [draft, setDraft] = useState<DishDraft>(createEmptyDraft([]));
  const [editingDishId, setEditingDishId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [disablingDishId, setDisablingDishId] = useState<number | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadAdminMenu() {
      try {
        const [categoriesData, dishesData] = await Promise.all([
          fetchCategories(),
          fetchAdminDishes(),
        ]);

        if (!isMounted) {
          return;
        }

        setCategories(categoriesData);
        setDishes(sortDishes(dishesData));
        setDraft(createEmptyDraft(categoriesData));
      } catch (error) {
        if (!isMounted) {
          return;
        }

        setNotice({
          tone: 'error',
          text: getApiErrorMessage(
            error,
            'Non sono riuscito a caricare la gestione menu per l\'area admin.',
          ),
        });
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadAdminMenu();

    return () => {
      isMounted = false;
    };
  }, []);

  function resetForm() {
    setEditingDishId(null);
    setDraft(createEmptyDraft(categories));
  }

  function handleTextChange(field: 'name' | 'description' | 'price' | 'categoryId', value: string) {
    setDraft((currentDraft) => ({
      ...currentDraft,
      [field]: value,
    }));
  }

  function handleToggleChange(field: 'isActive' | 'isAvailable', checked: boolean) {
    setDraft((currentDraft) => {
      if (field === 'isActive' && !checked) {
        return {
          ...currentDraft,
          isActive: false,
          isAvailable: false,
        };
      }

      return {
        ...currentDraft,
        [field]: checked,
      };
    });
  }

  function startEditingDish(dish: Dish) {
    setEditingDishId(dish.id);
    setDraft(createDraftFromDish(dish));
    setNotice(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const name = draft.name.trim();
    const description = draft.description.trim();
    const normalizedPrice = draft.price.replace(',', '.');
    const price = Number.parseFloat(normalizedPrice);
    const categoryId = Number.parseInt(draft.categoryId, 10);

    if (!name) {
      setNotice({
        tone: 'info',
        text: 'Inserisci il nome del piatto prima di salvare.',
      });
      return;
    }

    if (!Number.isFinite(price) || price <= 0) {
      setNotice({
        tone: 'info',
        text: 'Inserisci un prezzo valido maggiore di zero.',
      });
      return;
    }

    if (!Number.isInteger(categoryId)) {
      setNotice({
        tone: 'info',
        text: 'Seleziona una categoria valida per il piatto.',
      });
      return;
    }

    const payload: DishUpsertInput = {
      name,
      description,
      price,
      category: categoryId,
      isActive: draft.isActive,
      isAvailable: draft.isActive ? draft.isAvailable : false,
    };

    setIsSaving(true);
    setNotice(null);

    try {
      const savedDish =
        editingDishId === null
          ? await createAdminDish(payload)
          : await updateAdminDish(editingDishId, payload);

      setDishes((currentDishes) =>
        sortDishes([
          ...currentDishes.filter((dish) => dish.id !== savedDish.id),
          savedDish,
        ]),
      );
      resetForm();
      setNotice({
        tone: 'success',
        text:
          editingDishId === null
            ? `Piatto "${savedDish.name}" aggiunto con successo.`
            : `Piatto "${savedDish.name}" aggiornato con successo.`,
      });
    } catch (error) {
      setNotice({
        tone: 'error',
        text: getApiErrorMessage(
          error,
          editingDishId === null
            ? 'Non sono riuscito ad aggiungere il nuovo piatto.'
            : 'Non sono riuscito ad aggiornare il piatto selezionato.',
        ),
      });
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDisableDish(dish: Dish) {
    if (!dish.isActive) {
      return;
    }

    const shouldDisable = window.confirm(
      `Vuoi disabilitare "${dish.name}"? Il piatto verrà tolto dal menu cliente.`,
    );

    if (!shouldDisable) {
      return;
    }

    setDisablingDishId(dish.id);
    setNotice(null);

    try {
      await disableAdminDish(dish.id);
      setDishes((currentDishes) =>
        sortDishes(
          currentDishes.map((currentDish) =>
            currentDish.id === dish.id
              ? {
                  ...currentDish,
                  isActive: false,
                  isAvailable: false,
                }
              : currentDish,
          ),
        ),
      );

      if (editingDishId === dish.id) {
        resetForm();
      }

      setNotice({
        tone: 'success',
        text: `Piatto "${dish.name}" disabilitato dal menu.`,
      });
    } catch (error) {
      setNotice({
        tone: 'error',
        text: getApiErrorMessage(
          error,
          `Non sono riuscito a disabilitare il piatto "${dish.name}".`,
        ),
      });
    } finally {
      setDisablingDishId(null);
    }
  }

  return (
    <PageLayout
      title="Gestisci menu"
      subtitle="L'admin può aggiungere, modificare e disabilitare i piatti senza toccare il flusso cliente del menu."
      actions={
        <button
          type="button"
          className="button button--secondary"
          onClick={resetForm}
          disabled={isSaving}
        >
          Nuovo piatto
        </button>
      }
    >
      {notice ? (
        <section className={`status-banner status-banner--${notice.tone}`}>
          {notice.text}
        </section>
      ) : null}

      {isLoading ? (
        <section className="surface empty-state">
          <h2>Caricamento menu admin</h2>
          <p>Sto recuperando categorie e piatti gestibili dal backend.</p>
        </section>
      ) : (
        <section className="admin-menu-layout">
          <section className="admin-menu-list">
            {dishes.length === 0 ? (
              <article className="surface empty-state">
                <h2>Nessun piatto presente</h2>
                <p>Quando aggiungerai un piatto dal form admin, comparirà subito qui.</p>
              </article>
            ) : (
              dishes.map((dish) => (
                <article key={dish.id} className="surface admin-menu-card">
                  <div className="admin-menu-card__header">
                    <div>
                      <p className="eyebrow">{dish.categoryName}</p>
                      <h2>{dish.name}</h2>
                    </div>
                    <span
                      className={`availability${
                        dish.isActive && dish.isAvailable ? '' : ' availability--off'
                      }`}
                    >
                      {getDishStatusLabel(dish)}
                    </span>
                  </div>

                  <p className="admin-menu-card__description">
                    {dish.description || 'Nessuna descrizione disponibile.'}
                  </p>

                  <div className="admin-menu-card__footer">
                    <strong className="price-pill">{formatCurrency(dish.price)}</strong>
                    <div className="admin-menu-card__actions">
                      <button
                        type="button"
                        className="button button--secondary"
                        onClick={() => startEditingDish(dish)}
                        disabled={isSaving || disablingDishId === dish.id}
                      >
                        Modifica
                      </button>
                      <button
                        type="button"
                        className="button button--secondary"
                        onClick={() => handleDisableDish(dish)}
                        disabled={!dish.isActive || disablingDishId === dish.id || isSaving}
                      >
                        {disablingDishId === dish.id ? 'Disattivazione...' : 'Disabilita'}
                      </button>
                    </div>
                  </div>
                </article>
              ))
            )}
          </section>

          <aside className="surface admin-menu-form-panel">
            <div>
              <p className="eyebrow">
                {editingDishId === null ? 'Nuovo piatto' : `Modifica piatto #${editingDishId}`}
              </p>
              <h2>
                {editingDishId === null
                  ? 'Aggiungi un piatto al menu'
                  : 'Aggiorna il piatto selezionato'}
              </h2>
              <p className="muted-text">
                Le categorie arrivano dal backend. La disabilitazione rimuove il piatto dal menu
                cliente senza cancellarne la storia.
              </p>
            </div>

            {categories.length === 0 ? (
              <p className="note-box">
                Non ci sono categorie disponibili. Prima serve almeno una categoria nel backend.
              </p>
            ) : (
              <form className="form-grid" onSubmit={handleSubmit}>
                <label className="field">
                  <span>Nome piatto</span>
                  <input
                    className="input"
                    value={draft.name}
                    onChange={(event) => handleTextChange('name', event.target.value)}
                    placeholder="Es. Carbonara Burger"
                  />
                </label>

                <label className="field">
                  <span>Categoria</span>
                  <select
                    className="input"
                    value={draft.categoryId}
                    onChange={(event) => handleTextChange('categoryId', event.target.value)}
                  >
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Prezzo</span>
                  <input
                    className="input"
                    type="number"
                    min="0"
                    step="0.01"
                    value={draft.price}
                    onChange={(event) => handleTextChange('price', event.target.value)}
                    placeholder="0.00"
                  />
                </label>

                <label className="field">
                  <span>Descrizione</span>
                  <textarea
                    className="textarea"
                    value={draft.description}
                    onChange={(event) => handleTextChange('description', event.target.value)}
                    placeholder="Ingredienti, note o breve descrizione del piatto."
                  />
                </label>

                <div className="admin-menu-form__toggles">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.isActive}
                      onChange={(event) =>
                        handleToggleChange('isActive', event.target.checked)
                      }
                    />
                    <span>
                      Visibile nel menu
                      <small>Se disattivato, il piatto non compare più nel menu cliente.</small>
                    </span>
                  </label>

                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.isAvailable}
                      disabled={!draft.isActive}
                      onChange={(event) =>
                        handleToggleChange('isAvailable', event.target.checked)
                      }
                    />
                    <span>
                      Disponibile per l'ordine
                      <small>Usalo per segnare un piatto esaurito ma ancora visibile.</small>
                    </span>
                  </label>
                </div>

                <div className="admin-menu-form__actions">
                  <button
                    type="submit"
                    className="button button--primary"
                    disabled={isSaving}
                  >
                    {isSaving
                      ? editingDishId === null
                        ? 'Creazione...'
                        : 'Salvataggio...'
                      : editingDishId === null
                        ? 'Aggiungi piatto'
                        : 'Salva modifiche'}
                  </button>

                  {editingDishId !== null ? (
                    <button
                      type="button"
                      className="button button--secondary"
                      onClick={resetForm}
                      disabled={isSaving}
                    >
                      Annulla
                    </button>
                  ) : null}
                </div>
              </form>
            )}
          </aside>
        </section>
      )}
    </PageLayout>
  );
}
