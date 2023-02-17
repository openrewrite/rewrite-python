package org.openrewrite.python.experimental.tree.common;

import lombok.EqualsAndHashCode;
import lombok.Getter;

import java.util.Collection;
import java.util.Collections;
import java.util.function.BiFunction;
import java.util.function.Consumer;

@EqualsAndHashCode
public final class BetweenItemsList<TItem, TBetween> {
    public static <TItem, TBetween> BetweenItemsList<TItem, TBetween> empty() {
        return new BetweenItemsList<>(ItemList.from(Collections.emptyList()), ItemList.from(Collections.emptyList()));
    }

    public static <TItem, TBetween> BetweenItemsList<TItem, TBetween> from(Collection<TItem> items, Collection<TBetween> betweenItems) {
        return new BetweenItemsList<>(ItemList.from(items), ItemList.from(betweenItems));
    }

    @Getter
    private final ItemList<TItem> items;
    @Getter
    private final ItemList<TBetween> betweenItems;

    public <T> T reduce(T initial, BiFunction<T, TItem, T> onItem, BiFunction<T, TBetween, T> onBetween) {
        T value = initial;
        for (int i = 0; i < items.size(); i++) {
            value = onItem.apply(value, items.get(i));
            if (i < betweenItems.size()) {
                value = onBetween.apply(value, betweenItems.get(i));
            }
        }
        return value;
    }

    public void forEach(Consumer<TItem> onItem, Consumer<TBetween> onBetween) {
        for (int i = 0; i < items.size(); i++) {
            onItem.accept(items.get(i));
            if (i < betweenItems.size()) {
                onBetween.accept(betweenItems.get(i));
            }
        }
    }

    public BetweenItemsList(ItemList<TItem> items, ItemList<TBetween> betweenItems) {
        if (items.size() == 0 && betweenItems.size() != 0) {
            throw new IllegalArgumentException(
                    "if BetweenItemsList has no items, it should also have no betweenItems (found: " + betweenItems.size() + ")"
            );
        } else if (items.size() > 0 && betweenItems.size() != items.size() - 1) {
            throw new IllegalArgumentException(
                    "BetweenItemsList should have one fewer betweenItems (found " + betweenItems.size() + ") than items (found " + items.size() + ")"
            );
        }
        this.items = items;
        this.betweenItems = betweenItems;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        this.forEach(
                item -> sb.append(" ").append(item).append(" "),
                between -> sb.append(" ").append(between).append(" ")
        );
        sb.append("]");
        return sb.toString();
    }
}
