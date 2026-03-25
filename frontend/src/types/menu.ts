export type Category = {
  id: number;
  name: string;
};

export type Dish = {
  id: number;
  name: string;
  description: string;
  price: number;
  category: number;
  categoryName: string;
  isActive: boolean;
  isAvailable: boolean;
  imageUrl?: string;
};

export type DishUpsertInput = {
  name: string;
  description: string;
  price: number;
  category: number;
  isActive: boolean;
  isAvailable: boolean;
};
