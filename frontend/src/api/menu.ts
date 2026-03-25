import { apiClient } from './client';
import { attachDishImage } from '../content/menuPreview';
import type { Category, Dish, DishUpsertInput } from '../types/menu';

type CategoryApiItem = {
  id: number;
  name: string;
};

type DishApiItem = {
  id: number;
  name: string;
  description: string | null;
  price: number | string;
  category: number;
  category_name: string;
  is_active: boolean;
  is_available: boolean;
};

function mapDish(dish: DishApiItem): Dish {
  return attachDishImage({
    id: dish.id,
    name: dish.name,
    description: dish.description ?? '',
    price: Number(dish.price),
    category: dish.category,
    categoryName: dish.category_name,
    isActive: dish.is_active,
    isAvailable: dish.is_available,
  });
}

function mapDishPayload(input: DishUpsertInput) {
  return {
    name: input.name,
    description: input.description,
    price: input.price,
    category: input.category,
    is_active: input.isActive,
    is_available: input.isAvailable,
  };
}

export async function fetchCategories() {
  const response = await apiClient.get<CategoryApiItem[]>('categories/');

  return response.data.map((category) => ({
    id: category.id,
    name: category.name,
  })) satisfies Category[];
}

export async function fetchDishes() {
  const response = await apiClient.get<DishApiItem[]>('dishes/');

  return response.data.map(mapDish) satisfies Dish[];
}

export async function fetchAdminDishes() {
  const response = await apiClient.get<DishApiItem[]>('admin/dishes/');

  return response.data.map(mapDish) satisfies Dish[];
}

export async function createAdminDish(input: DishUpsertInput) {
  const response = await apiClient.post<DishApiItem>('admin/dishes/', mapDishPayload(input));

  return mapDish(response.data);
}

export async function updateAdminDish(dishId: number, input: DishUpsertInput) {
  const response = await apiClient.patch<DishApiItem>(
    `admin/dishes/${dishId}/`,
    mapDishPayload(input),
  );

  return mapDish(response.data);
}

export async function disableAdminDish(dishId: number) {
  await apiClient.delete(`admin/dishes/${dishId}/`);
}
